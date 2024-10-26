# utils/templates.py
from telegram import ReplyKeyboardMarkup, KeyboardButton
from typing import List

def generate_keyboard(buttons: List[List[str]]) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text) for text in row] for row in buttons]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
