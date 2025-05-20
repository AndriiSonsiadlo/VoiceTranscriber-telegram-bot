import asyncio

from dotenv import load_dotenv
from telegram import Update

load_dotenv()

AUTHORIZED_USER_IDS = [6089604978]


async def main() -> None:
    """Start the bot."""
    from bot import create_telegram_app

    application = await create_telegram_app()
    print("Starting bot...")

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


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
