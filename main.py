import os
import logging
import threading
import queue
import requests
import asyncio

from flask import Flask, request, jsonify

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("DAVID")


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


flask_app = Flask(__name__)

webhook_queue = queue.Queue(maxsize=100)

tg_app = None


def configuration_ok():
    missing = []

    if not TELEGRAM_TOKEN:
        missing.append("TELEGRAM_TOKEN")

    if not WEBHOOK_SECRET:
        missing.append("WEBHOOK_SECRET")

    if missing:
        logger.error(
            "Variabili Environment mancanti: %s",
            ", ".join(missing),
        )
    @flask_app.route("/", methods=["GET"])
def home():
    return "David CTO Core online.", 200


@flask_app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "agent": "David",
        }
    ), 200


@flask_app.route("/webhook", methods=["POST"])
def webhook():

    received_secret = request.headers.get("X-Webhook-Secret")

    if not WEBHOOK_SECRET:
        logger.error("WEBHOOK_SECRET non configurato.")
        return jsonify(
            {
                "status": "error",
                "message": "Server not configured",
            }
        ), 500

    if received_secret != WEBHOOK_SECRET:
        logger.warning("Webhook David rifiutato: secret non valido.")

        return jsonify(
            {
                "status": "error",
                "message": "Unauthorized",
            }
        ), 401

    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify(
                {
                    "status": "error",
                    "message": "Invalid JSON",
                }
            ), 400

        try:
            webhook_queue.put_nowait(data)

        except queue.Full:
            logger.error("Coda webhook David piena.")

            return jsonify(
                {
                    "status": "error",
                    "message": "Queue full",
                }
            ), 503

        logger.info("Webhook ricevuto da M.O.M.")

        return jsonify(
            {
                "status": "success",
                "agent": "David",
                "message": "Webhook queued",
            }
        ), 200

    except Exception:
        logger.exception("Errore durante la gestione del webhook.")

        return jsonify(
            {
                "status": "error",
                "message": "Internal server error",
            }
        ), 500
    def start_flask():
    try:
        port = int(os.getenv("PORT", "10000"))

        flask_app.run(
            host="0.0.0.0",
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True,
        )

    except Exception:
        logger.exception(
            "Errore avvio Flask David."
        )


async def webhook_worker(application):

    while True:

        try:
            data = await asyncio.to_thread(
                webhook_queue.get
            )

            if not isinstance(data, dict):
                continue

            chat_id = data.get("chat_id")

            if not chat_id:
                logger.warning(
                    "Webhook ricevuto senza chat_id."
                )
                continue

            message = (
                "🛠️ DAVID (CTO)\n\n"
                "Piano ricevuto da M.O.M. correttamente.\n\n"
                "Sto analizzando il piano dal punto di vista "
                "tecnico e infrastrutturale.\n\n"
                "Definirò backend, API, automazioni e "
                "componenti tecniche necessarie."
            )

            try:
                await application.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                )

                logger.info(
                    "Risposta inviata a Telegram. chat_id=%s",
                    chat_id,
                )

            except Exception:
                logger.exception(
                    "Errore invio Telegram David."
                )

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "Errore nel worker webhook David."
            )

            await asyncio.sleep(1)


async def post_init(application):

    application.create_task(
        webhook_worker(application)
)
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return

    await update.message.reply_text(
        "David (CTO) operativo.\n\n"
        "In attesa dei direttivi infrastrutturali "
        "di M.O.M."
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return

    chat = update.effective_chat

    if not chat:
        return

    # Nei gruppi David non risponde ai normali messaggi.
    # Riceve i piani direttamente tramite webhook di M.O.M.

    if chat.type in ("group", "supergroup"):
        return

    await update.message.reply_text(
        "David online.\n"
        "Sistemi di automazione, backend e API monitorati."
    )


def main():

    global tg_app

    if not configuration_ok():
        return

    threading.Thread(
        target=start_flask,
        daemon=True,
        name="DavidFlask",
    ).start()

    try:
        requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook",
            params={
                "drop_pending_updates": "true"
            },
            timeout=5,
        )

    except Exception:
        logger.warning(
            "Impossibile eseguire deleteWebhook."
        )

    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    tg_app = application

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    logger.info("David CTO avviato correttamente.")

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
