import os
import logging
from flask import Flask, request, jsonify
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

MODELS_TO_TRY = [
    "openrouter/free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "qwen/qwen3.8-27b:free",
    "google/gemma-4-26b-a4b-it:free"
]

SYSTEM_INSTRUCTION = """
Sei David, il Lead Tech Architect & Developer dell'ecosistema autonomo "Gor Hub".
Progetti, sviluppi, ottimizzi e mantieni l'intera infrastruttura software dell'ecosistema (Python, Flask, Telegram API, Render, OpenRouter, Persistenza dati e Webhooks).

IL TUO METODO OPERATIVO IN 3 PASSI:
1. Diagnosi & Architettura: Analizza i requisiti, individua la struttura di codice più solida, prevedendo persistenza dei dati, sicurezza e interconnessione tramite API/Webhook tra gli agenti (Mom, Ilaria, David).
2. Codice Clean, Resiliente e "Copy-Paste Ready": Fornisci sempre codice Python completo, ben commentato e pronto all'uso. Includi la gestione dei fallback multi-modello, gestione eccezioni (try-except) e threading sicuro tra Flask e Telegram.
3. Deployment & Infrastructure Kit: Insieme al codice, fornisci sempre:
   - Dipendenze per requirements.txt.
   - Variabili d'ambiente necessarie (.env).
   - Istruzioni per il deploy su Render, test Webhook e verifica dei log.

TONO E STILE:
- Pragmatico, sintetico, altamente tecnico ed essenziale. Zero preamboli: dai subito diagnosi e codice operativo.
"""

app_flask = Flask('')

@app_flask.route('/')
def home():
    return "David Tech Core is online."

@app_flask.route('/webhook', methods=['POST'])
def inter_agent_webhook():
    # Endpoint predisposto per la comunicazione futura tra agenti
    data = request.get_json() or {}
    logging.info(f"Ricevuto segnale inter-agente: {data}")
    return jsonify({"status": "received", "agent": "David"}), 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("David online, Leo. Architettura e Tech Core di Gor Hub pronti. Quale modulo o codice dobbiamo sviluppare?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = None

    for model_name in MODELS_TO_TRY:
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://davidgorbot.onrender.com",
                    "X-Title": "Gor Hub David"
                },
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": SYSTEM_INSTRUCTION},
                        {"role": "user", "content": user_text}
                    ]
                },
                timeout=30
            )
            res_json = response.json()
            if "choices" in res_json and len(res_json["choices"]) > 0:
                reply = res_json["choices"][0]["message"]["content"]
                break
        except Exception as e:
            logging.error(f"Errore con {model_name}: {e}")

    if reply:
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("DAVID: Errore di connessione al provider AI/OpenRouter.")

def main():
    if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
        print("ERRORE: Variabili d'ambiente mancanti su Render.")
        return

    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port, threaded=True, use_reloader=False)

if __name__ == "__main__":
    telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("David Bot in ascolto...")
    
    import threading
    t = threading.Thread(target=main)
    t.daemon = True
    t.start()

    telegram_app.run_polling()
