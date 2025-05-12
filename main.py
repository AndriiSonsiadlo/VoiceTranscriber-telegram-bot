from dotenv import load_dotenv
from fastapi import FastAPI
from telegram.ext import Application as TelegramApp

from bot import create_bot

load_dotenv()

fastapi_app: FastAPI = FastAPI()
telegram_app: TelegramApp


@fastapi_app.on_event("startup")
async def startup() -> None:
    """Initialize bot when FastAPI starts."""
    global telegram_app
    telegram_app = await create_bot()
