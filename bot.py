import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application as TelegramApp
from telegram.ext import CommandHandler, ContextTypes

load_dotenv()



async def create_telegram_app() -> TelegramApp:
    """Create and configure the bot application."""
    app = (
        TelegramApp.builder()
        .token(str(os.getenv("TELEGRAM_BOT_TOKEN")))
        .build()
    )
    app.add_handler(CommandHandler("start", start))

    return app


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command `/start` is issued."""
    if update.message:
        await update.message.reply_text(
            "Hi! I'm a Voice Transcription Bot.\n\n"
            "I'll transcribe voice messages and provide you with both the transcription and a summary!"
        )



