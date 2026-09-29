import os
import time
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_TOKEN = "8887715725:AAH2VJckKDyJcyV2-cEqhouimPnrtr8KZyo"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"David Dev AI is online!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

def ask_openrouter_developer(prompt):
    if not OPENROUTER_API_KEY:
        return "⚠️ Errore: OPENROUTER_API_KEY non trovata nelle Environment Variables di Render."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://gorhub.dev",
        "X-Title": "Gor Hub David Dev"
    }
    
    system_instruction = (
        "Sei David, il Lead Developer di Gor Hub. "
        "Rispondi sempre in italiano, in modo sintetico, preciso e altamente tecnico."
    )
    
    # Lista di modelli gratuiti su OpenRouter provati in sequenza
    models_to_try = [
        "mistralai/mistral-7b-instruct:free",
        "meta-llama/llama-3.2-11b-vision-instruct:free",
        "qwen/qwen-2-7b-instruct:free",
        "google/gemma-2-9b-it:free"
    ]
    
    for model_id in models_to_try:
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15)
            data = res.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            # Se c'è un errore di modello mancante/a pagamento, continua il ciclo ed entra nel modello successivo
        except Exception:
            continue

    return "Errore: Tutti i modelli gratuiti sono momentaneamente non disponibili. Riprova tra poco."

def get_updates(offset=None):
    try:
        response = requests.get(TELEGRAM_URL + "getUpdates", params={"timeout": 100, "offset": offset})
        return response.json()
    except Exception:
        return None

def send_message(chat_id, text):
    try:
        requests.post(TELEGRAM_URL + "sendMessage", data={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"Errore invio: {e}")

def main():
    print("🟢 David Dev (OpenRouter) avviato...")
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    last_update_id = None
    
    while True:
        updates = get_updates(last_update_id)
        if updates and "result" in updates:
            for update in updates["result"]:
                last_update_id = update["update_id"] + 1
                
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    
                    if text == "/start":
                        send_message(chat_id, "💻 **David (Gor Hub Lead Dev)** online. Dimmi pure!")
                    elif text == "/ping":
                        send_message(chat_id, "Pong 🟢 David Dev è online!")
                    else:
                        dev_response = ask_openrouter_developer(text)
                        send_message(chat_id, dev_response)
        
        time.sleep(1)

if __name__ == "__main__":
    main()
