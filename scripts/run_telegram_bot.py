# Create: scripts/run_telegram_bot.py
import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ingestion.telegram_bot import get_application

def main():
    # Get token from environment or .env file
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        try:
            from dotenv import load_dotenv
            load_dotenv(ROOT / ".env")
            token = os.getenv("TELEGRAM_BOT_TOKEN")
        except ImportError:
            pass

    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment or .env file.")
        print("Get a token from @BotFather on Telegram and add it to your .env file.")
        sys.exit(1)

    print("🤖 FORGE Telegram Bot is starting...")
    print("Open Telegram and search for your bot to test field updates.")
    
    app = get_application(token)
    app.run_polling()

if __name__ == "__main__":
    main()