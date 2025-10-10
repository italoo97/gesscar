from openai import OpenAI
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)
client2 = genai.configure(api_key=GEMINI_KEY)

def get_car_ai(model, brand, model_year):   
    message = ''''Faça uma descrição atrativa para o carro {} {} {} , Utilize apenas 250 caracteres que convencem o cliente.'''
    try:    
        message = message.format(brand, model, model_year)
        response = client.chat.completions.create(
            messages=[
                {
                    'role': 'user',
                    'content': message
                }
            ],
            max_tokens=1000,
            model= 'gpt-3.5-turbo',
        )
        return response.choices[0].message.content
    except Exception as e:
        response = client2.models.generate_content(
            model="gemini-2.5-flash",
            contents=message
        )
        return response.text
    
def get_ai_response(prompt, provider='chatgpt'):
    try:
        if provider == 'chatgpt':
            response = get_chatgpt_response(prompt)
            if error_response(response):
                return get_gemini_response(prompt)
            return response
        elif provider == 'gemini':
            return get_gemini_response(prompt)
        else:
            return f"Provider '{provider}' não reconhecido. Use 'chatgpt' ou 'gemini'."
    except Exception as e:
        print(f"Erro no provider {provider}: {e}")
        fallback_provider = 'gemini' if provider == 'chatgpt' else 'chatgpt'
        print(f"Tentando {fallback_provider} como fallback...")
        try:
            return get_ai_response(prompt, fallback_provider)
        except:
            return f"Erro ao conectar com ambos os providers de IA"

def get_chatgpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente virtual especializado em vendas de carros. Seja útil e amigável."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content

def get_gemini_response(prompt):
    message = f"Responda como um assistente virtual de concessionária: {prompt}"
    response = client2.models.generate_content(
        model="gemini-2.5-flash",
        contents=message
    )
    return response.text

def get_fallback_response(user_message):
    responses = {
        'horario': 'Funcionamos de Segunda a Sexta das 8h às 18h e Sábados das 8h às 12h.',
        'localizacao': 'Estamos localizados na Rua das Concessionárias, 123 - Centro, São Paulo - SP',
        'contato': 'Você pode nos contactar pelo telefone (11) 9999-9999 ou email contato@empresa.com',
        'carros': 'Temos uma variedade de carros usados e seminovos. Marque uma visita para conhecer nosso estoque!'
    }
    
    user_message_lower = user_message.lower()
    
    if 'horário' in user_message_lower or 'funciona' in user_message_lower:
        return responses['horario']
    elif 'local' in user_message_lower or 'endereço' in user_message_lower:
        return responses['localizacao']
    elif 'telefone' in user_message_lower or 'email' in user_message_lower or 'contato' in user_message_lower:
        return responses['contato']
    elif 'carro' in user_message_lower or 'estoque' in user_message_lower:
        return responses['carros']
    else:
        return "Desculpe, não entendi sua pergunta. Você pode perguntar sobre horários, localização, contato ou nossos carros disponíveis."
    
def error_response(response):
    if not response:
        return True
    error_indicators = ['erro', 'error', 'falha', 'failed', 'unavailable', 'indisponível']
    response_lower = response.lower()
    return any(indicator in response_lower for indicator in error_indicators)