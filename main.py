import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import Request, Response
from telegram import Update
from telegram.ext import Application as TelegramApp

from bot import create_telegram_app

load_dotenv()

fastapi_app: FastAPI = FastAPI()
telegram_app: TelegramApp


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan for bot initialization and cleanup."""
    global telegram_app
    telegram_app = await create_telegram_app()
    yield

fastapi_app.router.lifespan_context = lifespan


@fastapi_app.post("/api/webhook")
async def webhook(request: Request):
    """Handle incoming webhook requests from Telegram."""
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return Response(status_code=200)
    except Exception as e:
        return Response(content=str(e), status_code=500)


@fastapi_app.get("/api/set_webhook")
async def set_webhook():
    """Endpoint to set up the webhook."""
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        return {"error": "WEBHOOK_URL environment variable not set"}

    try:
        await telegram_app.bot.set_webhook(url=f"{webhook_url}")
        return {"message": "Webhook set successfully"}
    except Exception as e:
        return {"error": str(e)}
