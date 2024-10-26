# utils/openai_api.py
import aiohttp
import logging
import json
from config import OPENAI_API_KEY, API_URL

logger = logging.getLogger(__name__)

async def get_gpt_response(system_description: str, user_content: str, response_structure: dict) -> str:
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": system_description},
            {"role": "user", "content": f"Зроби повний опис героя відповідно до наступної структури:\n{json.dumps(response_structure, ensure_ascii=False, indent=2)}"}
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
                    error_text = await response.text()
                    logger.error(f"OpenAI API Error: {response.status} - {error_text}")
                    return "⚠️ Сталася помилка при зверненні до OpenAI API."
    except Exception as e:
        logger.error(f"Exception при зверненні до OpenAI API: {e}")
        return "⚠️ Сталася невідома помилка при обробці вашого запиту."
