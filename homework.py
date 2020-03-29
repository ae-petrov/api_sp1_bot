import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

API_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
PROXY = telegram.utils.request.Request(proxy_url='socks5://110.49.101.58:1080')

bot = telegram.Bot(token=TELEGRAM_TOKEN, request=PROXY)

def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    homework_statuses = {'homeworks': [], 'current_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    
    try:
        response = requests.get(API_URL, headers = headers, params = params)
        homework_statuses = response.json()
    except Exception as e:
        print(f'Что-то пошло не так при запросе — {e}')
    
    return homework_statuses


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            homeworks = new_homework.get('homeworks')
            if homeworks is None:
                return print(f'В ответе сервера отсутствует ключ ''homeworks''')
            else:
                send_message(parse_homework_status(homeworks[0]))
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут
        except KeyboardInterrupt:
            break
        except Exception as e:
            return print(f'Бот остановлен по причине: {e}')

if __name__ == '__main__':
    main()
