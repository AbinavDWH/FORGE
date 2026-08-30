# Create: app/ingestion/telegram_bot.py
import os
import logging
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
STORAGE_RAW = Path("storage/raw")
STORAGE_RAW.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends welcome message when user types /start."""
    await update.message.reply_text(
        "👷 *FORGE Site Assistant*\n\n"
        "Send me a voice note, photo, or text update.\n"
        "Example: _'Sector B Pier 14 concrete pouring completed.'_",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes incoming field updates and forwards to FORGE backend."""
    media_type = "text"
    raw_text = ""
    file_path = None
    
    # 1. Determine media type and download if necessary
    if update.message.voice:
        media_type = "voice"
        file = await context.bot.get_file(update.message.voice.file_id)
        file_path = STORAGE_RAW / f"{update.message.voice.file_id}.ogg"
        await file.download_to_drive(file_path)
        raw_text = update.message.text or "[Voice Note Received]"
    elif update.message.photo:
        media_type = "image"
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_path = STORAGE_RAW / f"{update.message.photo[-1].file_id}.jpg"
        await file.download_to_drive(file_path)
        raw_text = update.message.caption or "[Photo Received]"
    elif update.message.text:
        media_type = "text"
        raw_text = update.message.text
        
    await update.message.reply_text("⏳ _Sending to FORGE backend..._", parse_mode="Markdown")
    
    # 2. Forward to FastAPI Ingestion Endpoint
    try:
        async with httpx.AsyncClient() as client:
            files = {}
            data = {
                "source": "telegram",
                "media_type": media_type,
                "raw_text": raw_text
            }
            if file_path and file_path.exists():
                files["file"] = open(file_path, "rb")
                
            response = await client.post(f"{BACKEND_URL}/api/ingestion/upload", data=data, files=files)
            response.raise_for_status()
            result = response.json()
            
            ingestion_id = result.get("ingestion_id")
            
            await update.message.reply_text(
                f"✅ *Update Received*\n\n"
                f"*Ingestion ID:* `{ingestion_id}`\n"
                f"*Status:* Processing extraction and matching...\n\n"
                f"_You will be notified when the planner reviews it._",
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Backend error: {e}")
        await update.message.reply_text(
            "❌ *Failed to reach FORGE backend.*\n"
            "Is the server running on port 8000?",
            parse_mode="Markdown"
        )

def get_application(token: str) -> Application:
    """Builds the Telegram bot application."""
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.PHOTO, handle_message))
    return application