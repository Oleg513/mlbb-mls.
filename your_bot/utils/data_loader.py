# utils/data_loader.py
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

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
