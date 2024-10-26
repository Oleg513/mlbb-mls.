# main.py
import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from config import TELEGRAM_BOT_TOKEN
from handlers.main_menu import start, main_menu_handler
from handlers.characters import States as CharactersStates
from handlers.guides import States as GuidesStates
# Імпортуйте інші обробники...

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def setup_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            States.MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            # Додайте інші стани та обробники
        },
        fallbacks=[CommandHandler('start', start)]
    )

async def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Додаємо ConversationHandler
    conv_handler = setup_conversation_handler()
    application.add_handler(conv_handler)
    
    # Додаємо інші обробники, якщо потрібно
    
    # Додаємо обробник помилок
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(msg="Виникла помилка:", exc_info=context.error)
    application.add_error_handler(error_handler)
    
    logger.info("🔄 Бот запущено.")
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
