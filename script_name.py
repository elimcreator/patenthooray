import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Bot
import time
import asyncio
import logging
import random

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
COLUMN_INDEX = 3  # индекс столбца, который отслеживаем (начинается с 1)
TASK_COLUMN = 2  # индекс столбца с названием задачи (B)

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key('18jaRufkOwvRsZos5wB7IuRy-M79AdsIk9VvufLAThvA').worksheet('Темы')
    logging.info("Google Sheets connected successfully.")
except Exception as e:
    logging.error(f"Error while connecting to Google Sheets: {e}")

# Список из 100 комплиментов
compliments = [
    "Ты настоящий лидер!", "Ты всегда на высоте!", "Отличная работа, ты супер!",
    "Так держать, ты мастер своего дела!", "Твой вклад бесценен!", "Ты великолепен!",
    "Ты просто гений!", "Ты вдохновляешь всех вокруг!", "Твой потенциал безграничен!",
    "Ты отлично справляешься с любыми задачами!", "Ты всегда находишь верное решение!",
    "Ты креативен и находчив!", "Твоё умение решать проблемы поражает!", "Ты прирождённый победитель!",
    "Ты заслуживаешь похвалы за свою работу!", "Ты настоящий профессионал!", "Ты всегда находишь лучшее решение!",
    "Ты превзошёл все ожидания!", "Твоё внимание к деталям впечатляет!", "Ты приносишь позитив в любую ситуацию!",
    "Твои идеи гениальны!", "Ты умеешь управлять проектами лучше всех!", "Ты справляешься с любой задачей!",
    "Твоя целеустремлённость заслуживает уважения!", "Ты лучший в своём деле!", "Ты никогда не сдаёшься!",
    "Ты всегда на шаг впереди!", "Твоя настойчивость приносит результат!", "Ты обладаешь выдающимися способностями!",
    "Ты прирождённый лидер!", "Твои навыки и опыт бесценны!", "Ты всегда на высоте!",
    "Ты прекрасный мотиватор!", "Твоё отношение к работе впечатляет!", "Ты отличный наставник!",
    "Ты создаёшь вокруг себя атмосферу успеха!", "Ты умеешь находить решение даже в сложных ситуациях!",
    "Ты мастер в своём деле!", "Твои результаты говорят сами за себя!", "Ты достойный пример для подражания!",
    "Ты умеешь вдохновлять на подвиги!", "Твоя уверенность заряжает всех вокруг!", "Ты умело управляешь проектами!",
    "Ты подаёшь пример профессионализма!", "Твоя работа говорит сама за себя!", "Ты истинный мастер своего дела!",
    "Ты всегда справляешься с трудностями на ура!", "Ты достигаешь целей с невероятной лёгкостью!",
    "Ты воплощение успеха!", "Ты всегда находишь инновационные решения!", "Твоя работоспособность впечатляет!",
    "Ты умеешь решать задачи с минимальными затратами времени!", "Твои решения всегда точны!",
    "Ты заслуживаешь всех похвал за свою работу!", "Твой вклад бесценен для команды!", "Ты превосходишь все ожидания!",
    "Твои успехи достойны восхищения!", "Ты умело ведёшь проекты к победе!", "Твоя эффективность на высоте!",
    "Ты умеешь достигать целей легко и уверенно!", "Ты источник вдохновения для всех вокруг!",
    "Твоя настойчивость – ключ к успеху!", "Ты настоящий профессионал в своём деле!", "Ты пример для всех нас!",
    "Твоё стремление к совершенству восхищает!", "Ты всегда полон идей и решимости!", "Ты делаешь невозможное возможным!",
    "Ты всегда делаешь больше, чем ожидается!", "Ты вдохновляешь людей вокруг на свершения!",
    "Твоя энергия и энтузиазм заряжают!", "Ты всегда находишь новые пути решения проблем!",
    "Ты прирождённый стратег!", "Твои действия ведут команду к успеху!", "Твоя самоотдача заслуживает признания!",
    "Ты всегда доводишь дело до конца!", "Твоя работа приносит невероятные результаты!",
    "Ты становишься лучше с каждым днём!", "Ты умеешь решать любые задачи с лёгкостью!",
    "Ты создаёшь атмосферу успеха вокруг себя!", "Ты всегда готов к новым вызовам!",
    "Твои знания и опыт бесценны для команды!", "Ты вдохновляешь всех вокруг своим примером!",
    "Ты всегда находишь креативные решения!", "Ты двигаешься к успеху с невероятной скоростью!",
    "Твоя работоспособность на высшем уровне!", "Ты обладаешь уникальными способностями!",
    "Твоя уверенность и настойчивость вдохновляют!", "Ты всегда добиваешься своих целей!",
    "Ты светишься уверенностью и профессионализмом!", "Ты достигаешь успехов там, где другие сдаются!",
    "Ты источник вдохновения для всех вокруг!", "Ты полон энергии и готов к победам!",
    "Твоя упорная работа приносит потрясающие результаты!", "Ты всегда находишь инновационные решения!",
    "Ты становишься лучше с каждым днём!", "Твои достижения говорят сами за себя!"
]

# Хранение предыдущего состояния ячеек
previous_values = sheet.col_values(COLUMN_INDEX)
logging.info(f"Initial values in column {COLUMN_INDEX}: {previous_values}")

async def check_for_updates():
    global previous_values
    try:
        current_values = sheet.col_values(COLUMN_INDEX)
        logging.info(f"Current values in column {COLUMN_INDEX}: {current_values}")

        for row, value in enumerate(current_values):
            if value == "готово" and previous_values[row] != "готово":
                task_name = sheet.cell(row + 1, TASK_COLUMN).value  # Получаем название задачи из столбца B
                compliment = random.choice(compliments)  # Случайный комплимент
                logging.info(f"Change detected in row {row + 1}. Sending message to Telegram.")
                await send_telegram_message(task_name, compliment)
                previous_values[row] = value  # обновляем состояние ячеек
            else:
                logging.info(f"No changes detected in row {row + 1}.")
    except Exception as e:
        logging.error(f"Error while checking for updates: {e}")

async def send_telegram_message(task_name, compliment):
    message = f"Задача {task_name} готова! {compliment}"
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)  # Используем await для асинхронного вызова
        logging.info(f"Message sent to Telegram: {message}")
    except Exception as e:
        logging.error(f"Error while sending message to Telegram: {e}")

async def main():
    start_time = time.time()  # время запуска скрипта
    max_duration = 300  # максимальное время работы скрипта, 300 секунд (5 минут)

    logging.info("Script started.")

    while time.time() - start_time < max_duration:
        logging.info("Checking for updates...")
        await check_for_updates()
        logging.info("Sleeping for 10 seconds.")
        await asyncio.sleep(10)  # ждём 10 секунд между проверками
    
    logging.info("Script finished.")

if __name__ == "__main__":
    asyncio.run(main())
