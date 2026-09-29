import time
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_TOKEN = "8887715725:AAH2VJckKDyJcyV2-cEqhouimPnrtr8KZyo"
GROQ_API_KEY = "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"

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Mini server web per mantenere attivo Render Web Service
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"David Dev AI (Groq) is online!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

def ask_groq_developer(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    system_instruction = (
        "Sei David, il Lead Developer e assistente tecnico di Gor Hub. "
        "Sei un esperto di programmazione, architettura software e automazione. "
        "Rispondi in modo conciso, chiaro, diretto e con esempi di codice puliti quando richiesto."
    )
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }
    
    try:
        res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        data = res.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            print(f"Errore risposta Groq: {data}")
            return "Errore nella risposta del motore dev."
    except Exception as e:
        print(f"Errore Groq API: {e}")
        return "Ho riscontrato un problema di connessione con la mia AI."

def get_updates(offset=None):
    try:
        response = requests.get(TELEGRAM_URL + "getUpdates", params={"timeout": 100, "offset": offset})
        return response.json()
    except Exception as e:
        print(f"Errore di connessione: {e}")
        return None

def send_message(chat_id, text):
    try:
        requests.post(TELEGRAM_URL + "sendMessage", data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        requests.post(TELEGRAM_URL + "sendMessage", data={"chat_id": chat_id, "text": text})

def main():
    print("🟢 David (Developer AI) è in fase di avvio...")
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
                        send_message(chat_id, "💻 **David (Gor Hub Lead Dev)** online. Inviami codice, idee o quesiti tecnici!")
                    elif text == "/ping":
                        send_message(chat_id, "Pong 🟢 David Dev è operativo su Groq!")
                    else:
                        dev_response = ask_groq_developer(text)
                        send_message(chat_id, dev_response)
        
        time.sleep(1)

if __name__ == "__main__":
    main()
