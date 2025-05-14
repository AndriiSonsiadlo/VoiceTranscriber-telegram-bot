import os
import tempfile
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from groq.types.audio import Transcription
from groq.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from telegram import Update
from telegram.ext import Application as TelegramApp
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


async def create_telegram_app() -> TelegramApp:
    """Create and configure the bot application."""
    app = (
        TelegramApp.builder()
        .token(str(os.getenv("TELEGRAM_BOT_TOKEN")))
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    return app


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command `/start` is issued."""
    if update.message:
        await update.message.reply_text(
            "Hi! I'm a Voice Transcription Bot.\n\n"
            "I'll transcribe voice messages and provide you with both the transcription and a summary!"
        )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages and voice notes."""
    if not update.message or not update.message.voice:
        return

    try:
        status_message = await update.message.reply_text("🎵 Processing your voice note...")

        voice_file = await update.message.voice.get_file()
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
            await voice_file.download_to_drive(temp_file.name)
            temp_path = temp_file.name

        transcription = await transcribe_audio(temp_path)
        summary = await generate_summary(transcription.text)

        await status_message.edit_text(
            "📝 *Transcription:*\n"
            f"{transcription.text}\n\n"
            "📌 *Summary:*\n"
            f"{summary}",
            parse_mode='Markdown'
        )

        os.unlink(temp_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Sorry, an error occurred: {str(e)}")


async def transcribe_audio(file_path: str) -> Transcription:
    """Transcribe audio using Whisper via Groq API."""
    with open(file_path, "rb") as audio_file:
        completion = groq_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return completion


async def generate_summary(text: str) -> Any:
    """Generate a summary using LLama 3 via Groq API."""
    completion = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            ChatCompletionSystemMessageParam(
                content="Generate a concise summary of the following text:", role="system"
            ),
            ChatCompletionUserMessageParam(content=text, role="user")
        ]
    )
    return completion.choices[0].message.content