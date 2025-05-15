import asyncio

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes

from bot import create_telegram_app

load_dotenv()


async def main() -> None:
    """Start the bot."""
    application = await create_telegram_app()
    print("Starting bot...")
    application.add_error_handler(error_handler)

    try:
        await application.initialize()
        await application.start()

        if application.updater:
            await application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )

        print("Bot is running. Press Ctrl+C to stop.")

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        print("Stopping bot...")
        if application.updater:
            await application.updater.stop()
        await application.stop()
        print("Bot stopped.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
