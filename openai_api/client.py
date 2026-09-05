import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

import google.generativeai as genai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_KEY')

# Tempo maximo (em segundos) de espera por uma resposta de IA.
# Sem isso o chat fica travado no "digitando..." por minutos quando a API
# do provider esta lenta ou fora do ar.
AI_TIMEOUT = float(os.getenv('AI_TIMEOUT', '8'))

# Alguns SDKs (o do Gemini, por exemplo) fazem retries internos e ignoram o
# timeout pedido. Este executor garante um limite de tempo real por provider.
_executor = ThreadPoolExecutor(max_workers=4)


def _call_with_deadline(func, prompt):
    future = _executor.submit(func, prompt)
    try:
        return future.result(timeout=AI_TIMEOUT)
    except FutureTimeout:
        future.cancel()
        raise TimeoutError(f'Provider excedeu {AI_TIMEOUT}s.')

OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')


class AIUnavailableError(Exception):
    """Nenhum provider de IA conseguiu responder."""


# Os clientes sao criados sob demanda (lazy) e nao no import do modulo.
# Antes, um `OpenAI(api_key=None)` no topo do arquivo derrubava o projeto
# inteiro no boot quando o .env nao estava configurado.
_openai_client = None
_gemini_model = None


def get_openai_client():
    global _openai_client
    if not OPENAI_API_KEY:
        raise AIUnavailableError('OPENAI_API_KEY nao configurada.')
    if _openai_client is None:
        _openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=AI_TIMEOUT,
            max_retries=1,
        )
    return _openai_client


def get_gemini_model():
    global _gemini_model
    if not GEMINI_KEY:
        raise AIUnavailableError('GEMINI_KEY nao configurada.')
    if _gemini_model is None:
        genai.configure(api_key=GEMINI_KEY)
        _gemini_model = genai.GenerativeModel(GEMINI_MODEL)
    return _gemini_model


def get_chatgpt_response(prompt):
    response = get_openai_client().chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                'role': 'system',
                'content': (
                    'Voce e um assistente virtual especializado em vendas '
                    'de carros. Seja util e amigavel.'
                ),
            },
            {'role': 'user', 'content': prompt},
        ],
        max_tokens=500,
        temperature=0.7,
        timeout=AI_TIMEOUT,
    )
    return response.choices[0].message.content


def get_gemini_response(prompt):
    message = f'Responda como um assistente virtual de concessionaria: {prompt}'
    response = get_gemini_model().generate_content(
        message,
        request_options={'timeout': AI_TIMEOUT},
    )
    return response.text


def get_ai_response(prompt, provider='chatgpt'):
    """Consulta os providers de IA na ordem preferida.

    Levanta AIUnavailableError se nenhum responder, para que quem chama
    possa decidir o que fazer (ex.: usar get_fallback_response).
    """
    order = ['chatgpt', 'gemini'] if provider == 'chatgpt' else ['gemini', 'chatgpt']
    providers = {
        'chatgpt': get_chatgpt_response,
        'gemini': get_gemini_response,
    }

    if provider not in providers:
        raise AIUnavailableError(
            f"Provider '{provider}' nao reconhecido. Use 'chatgpt' ou 'gemini'."
        )

    for name in order:
        try:
            response = _call_with_deadline(providers[name], prompt)
        except Exception as exc:
            print(f'Erro no provider {name}: {exc}')
            continue
        if response and response.strip():
            return response
        print(f'Provider {name} devolveu resposta vazia.')

    raise AIUnavailableError('Nenhum provider de IA respondeu.')


def get_car_ai(model, brand, model_year):
    """Descricao de venda gerada por IA. Devolve None se a IA falhar."""
    prompt = (
        f'Faca uma descricao atrativa para o carro {brand} {model} '
        f'{model_year}. Utilize apenas 250 caracteres que convencam o cliente.'
    )
    try:
        return get_ai_response(prompt)
    except AIUnavailableError as exc:
        print(f'get_car_ai indisponivel: {exc}')
        return None


def get_fallback_response(user_message):
    """Respostas prontas usadas quando a IA esta fora do ar."""
    responses = {
        'horario': (
            'Funcionamos de Segunda a Sexta das 8h as 18h e '
            'Sabados das 8h as 12h.'
        ),
        'localizacao': (
            'Estamos localizados na Rua das Concessionarias, 123 - '
            'Centro, Sao Paulo - SP'
        ),
        'contato': (
            'Voce pode nos contactar pelo telefone (11) 9999-9999 ou '
            'email contato@gesscar.com'
        ),
        'carros': (
            'Temos uma variedade de carros usados e seminovos. '
            'Marque uma visita para conhecer nosso estoque!'
        ),
        'pagamento': (
            'Aceitamos entrada, financiamento, consorcio e carro na troca. '
            'Fale com a gente para simular as condicoes.'
        ),
    }

    text = (user_message or '').lower()

    keywords = (
        ('horario', ('horario', 'horário', 'funciona', 'aberto', 'abre')),
        ('localizacao', ('local', 'onde', 'endereco', 'endereço', 'fica')),
        ('contato', ('telefone', 'email', 'e-mail', 'contato', 'whats')),
        ('pagamento', ('pagamento', 'financia', 'parcela', 'consorcio', 'troca')),
        ('carros', ('carro', 'estoque', 'veiculo', 'veículo', 'modelo')),
    )

    for key, terms in keywords:
        if any(term in text for term in terms):
            return responses[key]

    return (
        'Desculpe, nao entendi sua pergunta. Voce pode perguntar sobre '
        'horarios, localizacao, contato, formas de pagamento ou nossos '
        'carros disponiveis.'
    )
