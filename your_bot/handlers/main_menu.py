# handlers/main_menu.py
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from enum import Enum, auto
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class States(Enum):
    MAIN_MENU = auto()
    # Інші стани...

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    logger.info("Користувач ініціював команду /start")
    buttons = [
        [KeyboardButton("🧙‍♂️ Персонажі"), KeyboardButton("📚 Гайди"), KeyboardButton("🏆 Турніри")],
        [KeyboardButton("🔄 Оновлення"), KeyboardButton("🆓 Початківець"), KeyboardButton("🔍 Пошук")],
        [KeyboardButton("📰 Новини"), KeyboardButton("💡 Допомога"), KeyboardButton("🎮 Вікторини")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("🔍 Оберіть опцію:", reply_markup=reply_markup)
    return States.MAIN_MENU

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір з головного меню: {user_input}")
    
    # Логіка переходів до підменю
    # Наприклад:
    if user_input == "🧙‍♂️ Персонажі":
        from handlers.characters import characters_menu
        return await characters_menu(update, context)
    elif user_input == "📚 Гайди":
        from handlers.guides import guides_menu
        return await guides_menu(update, context)
    # Додайте інші опції...
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.MAIN_MENU
