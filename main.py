from flask import Flask, render_template, request, jsonify
import requests
import logging

app = Flask(__name__, static_folder="assets")

# Configurar logging
logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    return render_template("contact.html")

@app.route("/enviar", methods=["POST", "OPTIONS"])
def enviar():
    if request.method == "OPTIONS":
        # Responde ao preflight CORS
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        data = request.get_json()
        
        # Verifica se recebeu dados JSON
        if not data:
            return jsonify({'erro': 'Nenhum dado JSON recebido'}), 400
        
        url = "https://script.google.com/macros/s/AKfycbyDTpJ0jzO8raesIVCnm9qj2amUSZCf-MwL9HpA6ckc0HrNC1Xo405-kDhtn907dMfSBw/exec"
        
        # Faz a requisição
        resposta = requests.post(url, json=data, timeout=30)
        
        # Log detalhado
        logging.info(f"Status Code: {resposta.status_code}")
        logging.info(f"Content-Type: {resposta.headers.get('Content-Type')}")
        
        # Tenta processar como JSON
        try:
            resposta_json = resposta.json()
            response = jsonify(resposta_json)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        except ValueError:
            response = jsonify({
                'erro': 'Resposta não é JSON válido',
                'resposta_original': resposta.text[:500]
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
            
    except Exception as e:
        logging.error(f"Erro: {str(e)}")
        response = jsonify({'erro': f'Erro interno: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)