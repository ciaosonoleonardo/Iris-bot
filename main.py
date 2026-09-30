import os
import logging
from flask import Flask, request, jsonify
import requests

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "David (CTO) Tech Core is online."

@app_flask.route('/webhook', methods=['POST'])
def inter_agent_webhook():
    data = request.get_json() or {}
    chat_id = data.get("chat_id")
    
    logging.info(f"David ha ricevuto il task da Mom: {data}")
    
    reply_text = (
        "🛠️ **DAVID (CTO)**: Direttive acquisite da Mom! "
        "Avvio immediato della configurazione tecnica dell'infrastruttura backend e gestione dei webhook."
    )
    
    if chat_id and TELEGRAM_TOKEN:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": reply_text,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload, timeout=10)
            logging.info(f"Risposta Telegram inviata da David. Status: {response.status_code}")
        except Exception as e:
            logging.error(f"Errore invio messaggio Telegram da David: {e}")
    else:
        logging.warning("Impossibile inviare il messaggio: chat_id o TELEGRAM_TOKEN mancanti.")
            
    return jsonify({"status": "executed", "agent": "David"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port, threaded=True)
