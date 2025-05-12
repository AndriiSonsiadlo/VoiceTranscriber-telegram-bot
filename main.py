from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from telegram.ext import Application as TelegramApp

from bot import create_bot

load_dotenv()

fastapi_app: FastAPI = FastAPI()
telegram_app: TelegramApp


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan for bot initialization and cleanup."""
    global telegram_app
    telegram_app = await create_bot()
    yield

fastapi_app.router.lifespan_context = lifespan
