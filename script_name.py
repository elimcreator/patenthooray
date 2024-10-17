import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Bot
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Настройка Telegram бота
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = Bot(token=TELEGRAM_TOKEN)

logging.info("Telegram bot initialized.")

# Настройка Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = 'credentials.json'  # Используем файл, который создаётся в GitHub Actions
COLUMN_INDEX = 2  # индекс столбца, который отслеживаем (начинается с 1)

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key('18jaRufkOwvRsZos5wB7IuRy-M79AdsIk9VvufLAThvA').worksheet('Темы')
    logging.info("Google Sheets connected successfully.")
except Exception as e:
    logging.error(f"Error while connecting to Google Sheets: {e}")

# Хранение предыдущего состояния ячеек
previous_values = sheet.col_values(COLUMN_INDEX)
logging.info(f"Initial values in column {COLUMN_INDEX}: {previous_values}")

def check_for_updates():
    global previous_values
    try:
        current_values = sheet.col_values(COLUMN_INDEX)
        logging.info(f"Current values in column {COLUMN_INDEX}: {current_values}")

        for row, value in enumerate(current_values):
            if value == "готово" and previous_values[row] != "готово":
                logging.info(f"Change detected in row {row + 1}. Sending message to Telegram.")
                send_telegram_message(row + 1)
                previous_values[row] = value  # обновляем состояние ячеек
            else:
                logging.info(f"No changes detected in row {row + 1}.")
    except Exception as e:
        logging.error(f"Error while checking for updates: {e}")

def send_telegram_message(row):
    message = f"Задача в строке {row} изменена на 'готово'."
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
        logging.info(f"Message sent to Telegram for row {row}.")
    except Exception as e:
        logging.error(f"Error while sending message to Telegram: {e}")

if __name__ == "__main__":
    start_time = time.time()  # время запуска скрипта
    max_duration = 300  # максимальное время работы скрипта, 300 секунд (5 минут)

    logging.info("Script started.")

    while time.time() - start_time < max_duration:
        logging.info("Checking for updates...")
        check_for_updates()
        logging.info("Sleeping for 10 seconds.")
        time.sleep(10)  # ждём 10 секунд между проверками
    
    logging.info("Script finished.")
