import os
import asyncio
import random
from telegram import Bot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Настройка Telegram бота
TELEGRAM_TOKEN = '7679103306:AAGFXZbpC2OZl5MIwU9i3KvcenaRJ4iDKT0'
CHAT_ID = '-1001622962509'
bot = Bot(token=TELEGRAM_TOKEN)

# Настройка Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = 'credentials.json'
COLUMN_INDEX_STATUS = 2  # Индекс столбца, где статус "готово"
COLUMN_INDEX_NAME = 1  # Индекс столбца B с названием задачи

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open_by_key('18jaRufkOwvRsZos5wB7IuRy-M79AdsIk9VvufLAThvA').worksheet('Темы')

# Хранение предыдущего состояния ячеек
previous_values = sheet.col_values(COLUMN_INDEX_STATUS)

# Список комплиментов
compliments = [
    "Ты настоящий лидер!",
    "Ты всегда на высоте!",
    "Отличная работа, ты супер!",
    "Так держать, ты мастер своего дела!",
    "Твой вклад бесценен!",
]

async def check_for_updates():
    global previous_values
    current_values = sheet.col_values(COLUMN_INDEX_STATUS)

    for row, value in enumerate(current_values):
        if value == "готово" and previous_values[row] != "готово":
            task_name = sheet.cell(row + 1, COLUMN_INDEX_NAME).value  # Получаем значение из столбца B
            compliment = random.choice(compliments)  # Случайный комплимент
            await send_telegram_message(task_name, compliment)
            previous_values[row] = value  # обновляем состояние ячеек

async def send_telegram_message(task_name, compliment):
    message = f"Задача {task_name} готова! {compliment}"
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"
