import os
import logging
import threading
import queue
import asyncio

from flask import Flask, request, jsonify

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("DAVID")


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


# ============================================================
# FLASK
# ============================================================

flask_app = Flask(__name__)


# Coda interna
webhook_queue = queue.Queue(
    maxsize=100
)


# Applicazione Telegram
tg_app = None


# ============================================================
# HOME
# ============================================================

@flask_app.route("/", methods=["GET"])
def home():

    return (
        "David CTO Core online.",
        200,
    )


# ============================================================
# HEALTH
# ============================================================

@flask_app.route("/health", methods=["GET"])
def health():

    return jsonify(
        {
            "status": "ok",
            "agent": "David",
        }
    ), 200


# ============================================================
# WEBHOOK
# ============================================================

@flask_app.route("/webhook", methods=["POST"])
def webhook():

    # --------------------------------------------------------
    # CONTROLLO SEGRETO
    # --------------------------------------------------------

    if not WEBHOOK_SECRET:

        logger.error(
            "WEBHOOK_SECRET non configurato."
        )

        return jsonify(
            {
                "status": "error",
                "message": "Server configuration error",
            }
        ), 500

    incoming_secret = request.headers.get(
        "X-MOM-Secret"
    )

    if incoming_secret != WEBHOOK_SECRET:

        logger.warning(
            "Tentativo webhook non autorizzato."
        )

        return jsonify(
            {
                "status": "error",
                "message": "Unauthorized",
            }
        ), 401

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    try:

        data = request.get_json(
            silent=True
        )

        if not isinstance(data, dict):

            return jsonify(
                {
                    "status": "error",
                    "agent": "David",
                    "message": "Invalid JSON",
                }
            ), 400

        # ----------------------------------------------------
        # DATI MINIMI OBBLIGATORI
        # ----------------------------------------------------

        chat_id = data.get("chat_id")
        full_plan = data.get("full_plan")

        if not chat_id or not full_plan:

            return jsonify(
                {
                    "status": "error",
                    "agent": "David",
                    "message": "Missing chat_id or full_plan",
                }
            ), 400

        # ----------------------------------------------------
        # CODA
        # ----------------------------------------------------

        try:

            webhook_queue.put_nowait(data)

        except queue.Full:

            logger.error(
                "Coda David piena. Payload rifiutato."
            )

            # NON restituiamo 200.
            # M.O.M. deve sapere che il payload
            # non è stato accettato.

            return jsonify(
                {
                    "status": "error",
                    "agent": "David",
                    "message": "Queue full",
                }
            ), 503

        logger.info(
            "Payload M.O.M. inserito nella coda."
        )

        # 202 = ricevuto e accettato per elaborazione
        return jsonify(
            {
                "status": "queued",
                "agent": "David",
                "message": "Webhook queued",
            }
        ), 202

    except Exception:

        logger.exception(
            "Errore webhook David."
        )

        return jsonify(
            {
                "status": "error",
                "agent": "David",
            }
        ), 500


# ============================================================
# FLASK SERVER
# ============================================================

def start_flask():

    try:

        port = int(
            os.getenv(
                "PORT",
                "10000",
            )
        )

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


# ============================================================
# WORKER
# ============================================================

async def webhook_worker():

    logger.info(
        "Worker webhook David avviato."
    )

    while True:

        try:

            # queue.Queue è bloccante.
            # Lo spostiamo fuori dall'event loop.

            data = await asyncio.to_thread(
                webhook_queue.get
            )

            try:

                if not isinstance(data, dict):
                    continue

                chat_id = data.get(
                    "chat_id"
                )

                full_plan = data.get(
                    "full_plan"
                )

                if not chat_id:
                    logger.warning(
                        "Payload senza chat_id."
                    )
                    continue

                if not full_plan:
                    logger.warning(
                        "Payload senza piano."
                    )
                    continue

                if not tg_app:

                    logger.error(
                        "tg_app non disponibile."
                    )

                    continue

                # ------------------------------------------------
                # MESSAGGIO TELEGRAM
                # ------------------------------------------------

                message = (
                    "🛠️ DAVID — CTO\n\n"
                    "Piano ricevuto da M.O.M. "
                    "correttamente.\n\n"
                    "Avvio l'analisi tecnica del piano "
                    "e la definizione delle attività "
                    "di infrastruttura, backend, API "
                    "e automazioni."
                )

                await tg_app.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                )

                logger.info(
                    "Conferma Telegram inviata da David."
                )

            finally:

                # Segnala alla queue che il lavoro
                # è stato consumato.
                webhook_queue.task_done()

        except asyncio.CancelledError:

            logger.info(
                "Worker David cancellato."
            )

            raise

        except Exception:

            logger.exception(
                "Errore nel worker David."
            )

            await asyncio.sleep(1)


# ============================================================
# POST INIT
# ============================================================

async def post_init(
    application
):

    application.create_task(
        webhook_worker()
    )


# ============================================================
# TELEGRAM /START
# ============================================================

async def start(
    update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return

    await update.message.reply_text(
        "David (CTO) operativo.\n\n"
        "In attesa dei direttivi "
        "infrastrutturali di M.O.M."
    )


# ============================================================
# TELEGRAM MESSAGES
# ============================================================

async def handle_message(
    update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return

    await update.message.reply_text(
        "David online.\n"
        "Sistemi di automazione, backend "
        "e API monitorati."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    global tg_app

    if not TELEGRAM_TOKEN:

        logger.error(
            "TELEGRAM_TOKEN mancante!"
        )

        return

    if not WEBHOOK_SECRET:

        logger.error(
            "WEBHOOK_SECRET mancante!"
        )

        return

    # Flask
    threading.Thread(
        target=start_flask,
        daemon=True,
        name="DavidFlask",
    ).start()

    # Telegram
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    tg_app = application

    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    logger.info(
        "David CTO avviato correttamente."
    )

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
