import os
import tempfile

from dotenv import load_dotenv
from groq import Groq
from groq.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from telegram import Update
from telegram.ext import Application as TelegramApp
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from main import AUTHORIZED_USER_IDS

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)

    return app


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command `/start` is issued."""
    if not update.effective_user or not update.message:
        return

    print(f"Received start command from user: {update.effective_user.id}")
    user_name = update.effective_user.first_name
    try:
        await update.message.reply_text(
            f"Hi, {user_name}! I'm a Voice Transcription Bot.\n\n"
            "I'll transcribe voice messages and provide you with both the transcription and a summary!"
        )
        print(f"Sent start message to user: {update.effective_user.id}")
    except Exception as e:
        print(f"Error sending start message to user {update.effective_user.id}: {str(e)}")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages and voice notes."""
    if not update.message or not update.message.voice or not update.effective_user:
        return

    try:
        if update.effective_user.id not in AUTHORIZED_USER_IDS:
            await update.message.reply_text("⛔ Sorry, you are not authorized to use this bot. Contact @andrii_sonsiadlo.")
            return

        status_message = await update.message.reply_text("🎵 Processing your voice note...")

        voice_file = await update.message.voice.get_file()
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
            await voice_file.download_to_drive(temp_file.name)
            temp_path = temp_file.name

        transcription = await transcribe_audio(temp_path)
        summary = await generate_summary(transcription)

        if len(transcription) > 3000:  # Leave room for summary and formatting
            await status_message.edit_text("📝 *Transcription (Part 1):*", parse_mode='Markdown')

            chunk_size = 4000
            transcription_chunks = [transcription[i:i + chunk_size]
                                    for i in range(0, len(transcription), chunk_size)]

            for i, chunk in enumerate(transcription_chunks, 1):
                await update.message.reply_text(
                    f"*Transcription (Part {i}):*\n{chunk}",
                    parse_mode='Markdown'
                )

            await update.message.reply_text(
                "📌 *Summary:*\n"
                f"{summary}",
                parse_mode='Markdown'
            )
        else:
            await status_message.edit_text(
                "📝 *Transcription:*\n"
                f"{transcription}\n\n"
                "📌 *Summary:*\n"
                f"{summary}",
                parse_mode='Markdown'
            )

        os.unlink(temp_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Sorry, an error occurred: {str(e)}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages and generate summaries."""
    if not update.effective_user or not update.message:
        return

    try:
        if update.effective_user.id not in AUTHORIZED_USER_IDS:
            await update.message.reply_text(
                "⛔ Sorry, you are not authorized to use this bot. Contact @andrii_sonsiadlo."
            )
            return

        status_message = await update.message.reply_text("📝 Generating summary...")
        text = update.message.text
        if not text:
            await status_message.edit_text("❌ Sorry, no text provided.")
            return

        summary = await generate_summary(text)
        await status_message.edit_text(
            "📌 *Summary:*\n"
            f"{summary}",
            parse_mode='Markdown'
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Sorry, an error occurred: {str(e)}")


async def transcribe_audio(file_path: str) -> str:
    """Transcribe audio using Whisper via Groq API."""
    with open(file_path, "rb") as audio_file:
        completion = groq_client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
            response_format="text"
        )
    return completion.text.strip()


async def generate_summary(text: str) -> str | None:
    """Generate a summary using LLama 3 via Groq API."""
    completion = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            ChatCompletionSystemMessageParam(
                content="Generate a concise summary of the following text:", role="system"
            ),
            ChatCompletionUserMessageParam(content=text, role="user")
        ],
        max_completion_tokens=32768
    )
    return completion.choices[0].message.content


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    print(f"Update {update} caused error {context.error}")
