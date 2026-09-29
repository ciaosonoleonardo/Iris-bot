import time
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "8887715725:AAH2VJckKDyJcyV2-cEqhouimPnrtr8KZyo"
URL = f"https://api.telegram.org/bot{TOKEN}/"

# Server dummy per far contento Render Web Service
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Iris is running!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

def get_updates(offset=None):
    try:
        response = requests.get(URL + "getUpdates", params={"timeout": 100, "offset": offset})
        return response.json()
    except Exception as e:
        print(f"Errore di connessione: {e}")
        return None

def send_message(chat_id, text):
    try:
        requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"Errore invio messaggio: {e}")

def main():
    print("🟢 Iris è in fase di avvio...")
    
    # Avvia il server web in un thread separato
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
                        send_message(chat_id, "Ciao! Sono Iris, il mozzo operativo di Gor Hub. 🚀")
                    elif text == "/ping":
                        send_message(chat_id, "Pong 🟢 Iris è online e pronta agli ordini!")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
