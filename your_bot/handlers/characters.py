# handlers/characters.py
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from enum import Enum, auto
from typing import Dict
import logging
from utils.data_loader import load_json_data
from utils.openai_api import get_gpt_response
from config import system_description, response_structure

logger = logging.getLogger(__name__)

class States(Enum):
    CHARACTERS_MENU = auto()
    # Інші стани...

heroes_data = load_json_data('data/heroes_tanks.json')
characters = load_json_data('data/characters.json')

async def characters_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    buttons = [
        [KeyboardButton("📝 Деталі про героїв"), KeyboardButton("🧩 Вгадай героя")],
        [KeyboardButton("⚔️ Порівняння героїв"), KeyboardButton("🎯 Контргерої")],
        [KeyboardButton("🗂 Список героїв"), KeyboardButton("🔙 Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("🧙‍♂️ Оберіть опцію:", reply_markup=reply_markup)
    return States.CHARACTERS_MENU

# Додайте інші обробники підменю, наприклад:
async def send_character_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Логіка відправки деталей про героя
    pass

# Інші функції...
