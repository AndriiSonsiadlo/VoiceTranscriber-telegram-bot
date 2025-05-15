import asyncio

from dotenv import load_dotenv
from telegram.ext import Application as TelegramApp

from bot import create_telegram_app

load_dotenv()


async def main() -> None:
    """Start the bot."""
    application = await create_telegram_app()
    print("Starting bot...")
    await application.initialize()
    await application.start()

    if application.updater:
        await application.updater.start_polling()

    print("Bot is running. Press Ctrl+C to stop.")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping bot...")
        if application.updater:
            await application.updater.stop()
        await application.stop()
        print("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")