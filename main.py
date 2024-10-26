import os
import json
import logging
import asyncio
from enum import Enum, auto
from typing import Dict

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
import aiohttp
from dotenv import load_dotenv
from string import Template

# Завантаження змінних оточення
load_dotenv()

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Визначення станів за допомогою Enum для кращої організації
class States(Enum):
    MAIN_MENU = auto()
    CHARACTERS_MENU = auto()
    GUIDES_MENU = auto()
    TOURNAMENTS_MENU = auto()
    UPDATES_MENU = auto()
    BEGINNER_MENU = auto()
    NEWS_MENU = auto()
    HELP_MENU = auto()
    QUIZZES_MENU = auto()
    SEARCH_PERFORMING = auto()
    SEARCH_HERO_GUIDES = auto()
    TANK_CHARACTERS_MENU = auto()

# Налаштування OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_URL = "https://api.openai.com/v1/chat/completions"

# Завантаження даних з файлів
def load_json_data(file_path: str) -> Dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if not data:
                raise ValueError(f"JSON файл {file_path} порожній.")
            return data
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не знайдено.")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Некоректний JSON в файлі {file_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Не вдалося завантажити файл {file_path}: {e}")
        return {}

heroes_data = load_json_data('heroes_tanks.json')
passive_skills = load_json_data('passive_skills.json')
menu_requests = load_json_data('menu_requests.json')
characters = load_json_data('characters.json')
prompts_data = load_json_data('prompts.json')

# Отримання system_prompt
system_prompt = prompts_data.get('system_prompt', {})
system_description = system_prompt.get('description', '')
response_structure = system_prompt.get('response_structure', {})

# Завантаження шаблону HTML
def load_html_template(file_path: str) -> Template:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
            return Template(template_content)
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не знайдено.")
        return Template("")
    except Exception as e:
        logger.error(f"Не вдалося завантажити файл {file_path}: {e}")
        return Template("")

html_template = load_html_template('prompts_message.html')

# Словник для зберігання вибраних героїв (може бути корисним для різних користувачів)
selected_heroes = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Користувач ініціював команду /start")
    buttons = [
        [KeyboardButton("🧙‍♂️ Персонажі"), KeyboardButton("📚 Гайди"), KeyboardButton("🏆 Турніри")],
        [KeyboardButton("🔄 Оновлення"), KeyboardButton("🆓 Початківець"), KeyboardButton("🔍 Пошук")],
        [KeyboardButton("📰 Новини"), KeyboardButton("💡 Допомога"), KeyboardButton("🎮 Вікторини")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("🔍 Оберіть опцію:", reply_markup=reply_markup)
    return States.MAIN_MENU

# Обробник повідомлень для основного меню
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір з головного меню: {user_input}")
    
    if user_input == "🧙‍♂️ Персонажі":
        # Перехід до підменю Персонажів
        buttons = [
            [KeyboardButton("📝 Деталі про героїв"), KeyboardButton("🧩 Вгадай героя")],
            [KeyboardButton("⚔️ Порівняння героїв"), KeyboardButton("🎯 Контргерої")],
            [KeyboardButton("🗂 Список героїв"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🧙‍♂️ Оберіть опцію:", reply_markup=reply_markup)
        return States.CHARACTERS_MENU
    elif user_input == "📚 Гайди":
        # Перехід до підменю Гайдів
        buttons = [
            [KeyboardButton("📝 Початок гри"), KeyboardButton("🔄 Продовження гри")],
            [KeyboardButton("📈 Розвиток"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("📚 Оберіть гайд:", reply_markup=reply_markup)
        return States.GUIDES_MENU
    elif user_input == "🏆 Турніри":
        # Перехід до підменю Турнірів
        buttons = [
            [KeyboardButton("📅 Графік турнірів"), KeyboardButton("🎖️ Результати")],
            [KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🏆 Оберіть опцію:", reply_markup=reply_markup)
        return States.TOURNAMENTS_MENU
    elif user_input == "🔄 Оновлення":
        # Перехід до підменю Оновлень
        buttons = [
            [KeyboardButton("🆕 Нові герої"), KeyboardButton("🛠️ Оновлення геймплею")],
            [KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🔄 Оновлення:", reply_markup=reply_markup)
        return States.UPDATES_MENU
    elif user_input == "🆓 Початківець":
        # Перехід до підменю Початківця
        buttons = [
            [KeyboardButton("📚 Основи гри"), KeyboardButton("🎮 Інтерактивні завдання")],
            [KeyboardButton("📈 Поради для прогресу"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🆓 Початківець:", reply_markup=reply_markup)
        return States.BEGINNER_MENU
    elif user_input == "🔍 Пошук":
        # Перехід до підменю Пошуку
        buttons = [
            [KeyboardButton("🔍 Пошук героїв та гайдів"), KeyboardButton("🎙️ Голосовий пошук")],
            [KeyboardButton("📝 Історія пошуку"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🔍 Пошук:", reply_markup=reply_markup)
        return States.SEARCH_PERFORMING
    elif user_input == "📰 Новини":
        # Перехід до підменю Новин
        buttons = [
            [KeyboardButton("📢 Останні новини"), KeyboardButton("🗞️ Архів новин")],
            [KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("📰 Новини:", reply_markup=reply_markup)
        return States.NEWS_MENU
    elif user_input == "💡 Допомога":
        # Перехід до підменю Допомоги
        buttons = [
            [KeyboardButton("❓ Часті питання"), KeyboardButton("📞 Контакти підтримки")],
            [KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("💡 Допомога:", reply_markup=reply_markup)
        return States.HELP_MENU
    elif user_input == "🎮 Вікторини":
        # Перехід до підменю Вікторин
        buttons = [
            [KeyboardButton("🧠 Вгадай цитату"), KeyboardButton("💥 Вгадай здібність")],
            [KeyboardButton("📚 Тест на знання"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🎮 Вікторини:", reply_markup=reply_markup)
        return States.QUIZZES_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.MAIN_MENU

# Визначення функції handle_characters_menu
async def handle_characters_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Персонажах: {user_input}")
    
    if user_input == "📝 Деталі про героїв":
        await send_character_details(update, context)
        return States.CHARACTERS_MENU
    elif user_input == "🧩 Вгадай героя":
        await start_quiz_guess_hero(update, context)
        return States.CHARACTERS_MENU
    elif user_input == "⚔️ Порівняння героїв":
        await send_character_comparison(update, context)
        return States.CHARACTERS_MENU
    elif user_input == "🎯 Контргерої":
        await send_counter_strategies(update, context)
        return States.CHARACTERS_MENU
    elif user_input == "🗂 Список героїв":
        await select_hero_class(update, context)
        return States.CHARACTERS_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        # Припустимо, що користувач вибрав конкретного героя
        hero_info = get_hero_info(user_input)
        if hero_info:
            gpt_response = await handle_gpt_query(hero_info['name'], context)
            await update.message.reply_text(gpt_response, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            return States.CHARACTERS_MENU
        else:
            await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
            return States.CHARACTERS_MENU

# Функція для вибору класу героя
async def select_hero_class(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    classes = list(characters.keys())
    buttons = []
    for cls in classes:
        buttons.append([KeyboardButton(cls)])
    buttons.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("🗂 **Оберіть клас героя:**", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    return States.CHARACTERS_MENU

# Функція для обробки вибору класу та відображення героїв
async def handle_hero_class_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_class = update.message.text
    logger.info(f"Вибір класу: {selected_class}")
    
    if selected_class in characters:
        heroes_list = characters[selected_class]
        buttons = []
        for hero in heroes_list:
            buttons.append([KeyboardButton(hero['uk'])])
            # Додаємо по 4 героїв в ряд
            if len(buttons[-1]) == 4:
                continue
        buttons.append([KeyboardButton("🔙 Назад")])
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text(f"🗂 **Список героїв класу {selected_class}:**", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        return States.CHARACTERS_MENU
    elif selected_class == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.CHARACTERS_MENU

# Функція для відправки деталей про героя через GPT-4
async def send_character_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Тут можна додати логіку для вибору конкретного героя або показати загальні деталі
    await update.message.reply_text("⚠️ Будь ласка, оберіть конкретного героя для перегляду деталей.", reply_markup=ReplyKeyboardMarkup(
        [[KeyboardButton("🔙 Назад")]], resize_keyboard=True, one_time_keyboard=False
    ))

# Функція для формування відповіді від GPT-4
async def handle_gpt_query(hero_name: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    # Отримання інформації про героя
    hero_info = get_hero_info(hero_name)
    if not hero_info:
        return "⚠️ Не вдалося знайти інформацію про цього героя."

    # Отримання пасивної навички
    passive_skill = get_passive_skill(hero_name)

    # Підготовка даних для запиту
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": system_description},
            {"role": "user", "content": f"Зроби повний опис героя {hero_name} відповідно до наступної структури:\n{json.dumps(response_structure, ensure_ascii=False, indent=2)}"}
        ],
        "max_tokens": 1500
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    assistant_reply = response_data['choices'][0]['message']['content']
                    return assistant_reply
                else:
                    logger.error(f"OpenAI API Error: {response.status} - {await response.text()}")
                    return "⚠️ Сталася помилка при зверненні до OpenAI API."
    except Exception as e:
        logger.error(f"Exception при зверненні до OpenAI API: {e}")
        return "⚠️ Сталася невідома помилка при обробці вашого запиту."

# Функція для отримання інформації про героя
def get_hero_info(hero_name: str) -> Dict:
    hero = next((hero for hero in heroes_data.get('heroes', []) if hero['name'].lower() == hero_name.lower()), None)
    if hero:
        required_fields = ["name", "class", "role", "speed", "hp", "physical_defense", "magical_defense", "attack_speed", "skills", "strategies", "recommendations", "drafts"]
        for field in required_fields:
            if field not in hero:
                logger.warning(f"Герой {hero_name} не має поля {field}.")
                hero[field] = "Невідомо"
    return hero

# Функції для інших підменю
# Наприклад, для Гайдів, Турнірів, Оновлень, Початківця, Пошуку, Новин, Допомоги, Вікторин

# Пример: Функція для обробки Гайдів
async def handle_guides_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Гайдах: {user_input}")
    
    if user_input == "📝 Початок гри":
        guides = "📚 **Гайд: Початок гри**\n\nОсь кілька порад для початку гри..."
        await update.message.reply_text(guides, parse_mode=ParseMode.MARKDOWN)
        return States.GUIDES_MENU
    elif user_input == "🔄 Продовження гри":
        guides = "📚 **Гайд: Продовження гри**\n\nОсь кілька порад для продовження гри..."
        await update.message.reply_text(guides, parse_mode=ParseMode.MARKDOWN)
        return States.GUIDES_MENU
    elif user_input == "📈 Розвиток":
        guides = "📚 **Гайд: Розвиток**\n\nОсь кілька порад для розвитку..."
        await update.message.reply_text(guides, parse_mode=ParseMode.MARKDOWN)
        return States.GUIDES_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.GUIDES_MENU

# Інші функції для обробки підменю Турнірів, Оновлень, Початківця, Пошуку, Новин, Допомоги, Вікторин
# Наприклад, функція для Початківця
async def handle_beginner_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Початківця: {user_input}")
    
    if user_input == "📚 Основи гри":
        guides = "📈 **Основи гри**\n\nОсновні елементи гри включають..."
        await update.message.reply_text(guides, parse_mode=ParseMode.MARKDOWN)
        return States.BEGINNER_MENU
    elif user_input == "🎮 Інтерактивні завдання":
        tasks = "🎯 **Інтерактивні завдання:**\n\nВиконайте наступні завдання..."
        await update.message.reply_text(tasks, parse_mode=ParseMode.MARKDOWN)
        return States.BEGINNER_MENU
    elif user_input == "📈 Поради для прогресу":
        tips = "📈 **Поради для прогресу:**\n\n• Практикуйтеся регулярно.\n• Аналізуйте свої матчі..."
        await update.message.reply_text(tips, parse_mode=ParseMode.MARKDOWN)
        return States.BEGINNER_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.BEGINNER_MENU

# Функція для обробки вибору конкретного героя
async def handle_hero_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_hero = update.message.text.strip()
    logger.info(f"Вибір героя: {selected_hero}")
    
    # Знайти героя за українською назвою
    hero = next((hero for hero in heroes_data.get('heroes', []) if hero['name'].lower() == selected_hero.lower()), None)
    
    if hero:
        gpt_response = await handle_gpt_query(hero['name'], context)
        await update.message.reply_text(gpt_response, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return States.CHARACTERS_MENU
    elif selected_hero == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Вибрана опція не відповідає жодному герою.")
        return States.CHARACTERS_MENU

# Обробник тригерних слів
TRIGGER_WORDS = ["герой", "персонаж", "геймплей", "MLBB", "mobile legends"]  # Приклад тригерних слів

async def trigger_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    message_text = update.message.text.lower()

    if any(trigger in message_text for trigger in TRIGGER_WORDS):
        # Вибір випадкового героя
        hero = random.choice(heroes_data.get('heroes', []))
        hero_name = hero['name']
        gpt_response = await handle_gpt_query(hero_name, context)
        await update.message.reply_text(gpt_response, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

# Функція для обробки повідомлень з тригерними словами
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    message_text = update.message.text.lower()

    if any(trigger in message_text for trigger in TRIGGER_WORDS):
        await trigger_handler(update, context)

# Функція для обробки невідомих команд
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("⚠️ Вибачте, я не розумію цю команду. Будь ласка, оберіть опцію з клавіатури.")

# Основна функція запуску бота
async def main():
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ Не встановлено TELEGRAM_BOT_TOKEN в змінних оточення.")
        exit(1)
    if not OPENAI_API_KEY:
        logger.error("❌ Не встановлено OPENAI_API_KEY в змінних оточення.")
        exit(1)
    
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))
    
    # Додаємо ConversationHandler для складних сценаріїв
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            States.MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            States.CHARACTERS_MENU: [
                MessageHandler(filters.Regex(f"^({'|'.join([hero['uk'] for hero in heroes_data.get('heroes', [])])})$"), handle_hero_selection),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_characters_menu)
            ],
            States.GUIDES_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guides_menu)],
            States.BEGINNER_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_beginner_menu)],
            # Додайте інші стани тут за потребою
        },
        fallbacks=[CommandHandler('start', start)]
    )
    application.add_handler(conv_handler)
    
    # Додаємо обробник тригерних слів
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Додаємо обробник невідомих команд
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Додаємо обробник помилок
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(msg="Виникла помилка:", exc_info=context.error)
    application.add_error_handler(error_handler)
    
    logger.info("🔄 Бот запущено.")
    await application.run_polling()

# Запуск бота
if __name__ == '__main__':
    import random
    asyncio.run(main())
