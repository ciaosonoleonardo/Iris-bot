import os
import time
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_TOKEN = "8887715725:AAH2VJckKDyJcyV2-cEqhouimPnrtr8KZyo"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"David Dev AI is online!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

def ask_groq_developer(prompt):
    if not GROQ_API_KEY:
        return "Errore: GROQ_API_KEY non trovata nelle variabili d'ambiente di Render."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    system_instruction = (
        "Sei David, il Lead Developer di Gor Hub. "
        "Rispondi sempre in italiano, in modo sintetico, preciso e tecnico."
    )
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        data = res.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            return f"Errore API Groq: {data['error'].get('message', 'Errore sconosciuto')}"
        else:
            return "Risposta non valida da Groq."
    except Exception as e:
        return f"Errore di connessione: {e}"

def get_updates(offset=None):
    try:
        response = requests.get(TELEGRAM_URL + "getUpdates", params={"timeout": 100, "offset": offset})
        return response.json()
    except Exception as e:
        return None

def send_message(chat_id, text):
    try:
        requests.post(TELEGRAM_URL + "sendMessage", data={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"Errore invio: {e}")

def main():
    print("🟢 David Dev è pronto...")
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
                        dev_response = ask_groq_developer(text)
                        send_message(chat_id, dev_response)
        
        time.sleep(1)

if __name__ == "__main__":
    main()
