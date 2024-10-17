import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Bot
import time

# Настройка Telegram бота
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = Bot(token=TELEGRAM_TOKEN)

# Настройка Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = 'credentials.json'  # Используем файл, который создаётся в GitHub Actions
COLUMN_INDEX = 3  # индекс столбца, который отслеживаем (начинается с 1)

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open_by_key('18jaRufkOwvRsZos5wB7IuRy-M79AdsIk9VvufLAThvA').worksheet('Темы')

# Хранение предыдущего состояния ячеек
previous_values = sheet.col_values(COLUMN_INDEX)

def check_for_updates():
    global previous_values
    current_values = sheet.col_values(COLUMN_INDEX)
    
    for row, value in enumerate(current_values):
        if value == "готово" and previous_values[row] != "готово":
            send_telegram_message(row + 1)
            previous_values[row] = value

def send_telegram_message(row):
    message = f"Задача в строке {row} изменена на 'готово'."
    bot.send_message(chat_id=CHAT_ID, text=message)

# Основной цикл программы
if __name__ == "__main__":
    while True:
        check_for_updates()
        time.sleep(10)  # проверяем каждые 10 секунд
