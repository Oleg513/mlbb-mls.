# handlers/guides.py
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from enum import Enum, auto
from typing import Dict
import logging
from utils.data_loader import load_json_data

logger = logging.getLogger(__name__)

class States(Enum):
    GUIDES_MENU = auto()
    CLASS_SELECTION = auto()
    INTERACTIVE_RECOMMENDATIONS = auto()
    # Інші стани...

guides_data = load_json_data('data/menu_requests.json')  # Припустимо, тут зберігаються меню гайдів

async def guides_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    buttons = [
        [KeyboardButton("📝 Стратегії для кожного класу"), KeyboardButton("💡 Інтерактивні рекомендації")],
        [KeyboardButton("🎥 Відео-гайди"), KeyboardButton("🔙 Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("📚 Оберіть опцію:", reply_markup=reply_markup)
    return States.GUIDES_MENU

async def send_class_strategies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    strategies = guides_data.get('class_strategies', "Немає доступних даних.")
    await update.message.reply_text(strategies, parse_mode='HTML', disable_web_page_preview=True)

async def send_interactive_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    classes = ["Танк", "Борець", "Маг", "Стрілець", "Асасин", "Підтримка"]
    buttons = []
    for i in range(0, len(classes), 3):
        row = classes[i:i + 3]
        buttons.append([KeyboardButton(cls) for cls in row])
    buttons.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("💡 **Оберіть клас, щоб отримати рекомендації гайдів:**", parse_mode='Markdown', reply_markup=reply_markup)
    return States.INTERACTIVE_RECOMMENDATIONS

async def handle_interactive_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_class = update.message.text.strip()
    classes = ["Танк", "Борець", "Маг", "Стрілець", "Асасин", "Підтримка"]
    if selected_class in classes:
        recommendations = f"💡 **Рекомендації гайдів для класу {selected_class}:**\n\n" \
                           f"• [Гайд для {selected_class} 1](https://example.com/guide-{selected_class.lower()}-1)\n" \
                           f"• [Гайд для {selected_class} 2](https://example.com/guide-{selected_class.lower()}-2)\n\n" \
                           f"🔗 Детальніше: https://example.com/recommendations-{selected_class.lower()}"
        await update.message.reply_text(recommendations, parse_mode='Markdown', disable_web_page_preview=True)
        # Повернення до інтерактивних рекомендацій
        buttons = []
        for i in range(0, len(classes), 3):
            row = classes[i:i + 3]
            buttons.append([KeyboardButton(cls) for cls in row])
        buttons.append([KeyboardButton("🔙 Назад")])
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("💡 **Оберіть клас, щоб отримати рекомендації гайдів:**", parse_mode='Markdown', reply_markup=reply_markup)
        return States.INTERACTIVE_RECOMMENDATIONS
    elif selected_class == "🔙 Назад":
        buttons = [
            [KeyboardButton("📝 Стратегії для кожного класу"), KeyboardButton("💡 Інтерактивні рекомендації")],
            [KeyboardButton("🎥 Відео-гайди"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("📚 Оберіть опцію:", reply_markup=reply_markup)
        return States.GUIDES_MENU
    else:
        await update.message.reply_text("⚠️ Вибрана опція не відповідає жодному класу.")
        return States.INTERACTIVE_RECOMMENDATIONS

async def send_video_guides(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    video_guides = guides_data.get('video_guides', "Немає доступних даних.")
    await update.message.reply_text(video_guides, parse_mode='Markdown', disable_web_page_preview=True)

async def handle_guides_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Гайдах: {user_input}")
    
    if user_input == "📝 Стратегії для кожного класу":
        await send_class_strategies(update, context)
        return States.GUIDES_MENU
    elif user_input == "💡 Інтерактивні рекомендації":
        return await send_interactive_recommendations(update, context)
    elif user_input == "🎥 Відео-гайди":
        await send_video_guides(update, context)
        return States.GUIDES_MENU
    elif user_input == "🔙 Назад":
        from handlers.main_menu import start
        return await start(update, context)
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.GUIDES_MENU
