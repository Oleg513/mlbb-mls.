# config.py
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_URL = "https://api.openai.com/v1/chat/completions"

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Не встановлено TELEGRAM_BOT_TOKEN в змінних оточення.")
if not OPENAI_API_KEY:
    raise ValueError("Не встановлено OPENAI_API_KEY в змінних оточення.")
