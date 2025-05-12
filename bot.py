import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application as Bot
from telegram.ext import CommandHandler, ContextTypes

load_dotenv()


def create_bot() -> Bot:
    """Create and configure the bot application."""
    bot = (
        Bot.builder()
        .token(str(os.getenv("TELEGRAM_BOT_TOKEN")))
        .updater(None)  # no updater needed for webhook
        .build()
    )
    bot.add_handler(CommandHandler("start", start))

    return bot


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command `/start` is issued."""
    if update.message:
        await update.message.reply_text(
            "Hi! I'm a Voice Transcription Bot.\n\n"
            "I'll transcribe voice messages and provide you with both the transcription and a summary!"
        )


application: Bot = create_bot()
