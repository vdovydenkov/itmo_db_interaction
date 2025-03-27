import json
import psycopg2
import os

file_path = os.path.dirname(os.path.abspath(__file__))
USERS_FILE_NAME = os.path.join(file_path, 'users.json')
CALENDARS_FILE_NAME = os.path.join(file_path, 'calendars.json')
EVENTS_FILE_NAME = os.path.join(file_path, 'events.json')

def read_from_json(filename):
    print(f'Читаем {filename}')
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

try:
    users = read_from_json(USERS_FILE_NAME)
    calendars = read_from_json(CALENDARS_FILE_NAME)
    events = read_from_json(EVENTS_FILE_NAME)
except Exception as err:
    print(f'Ошибка чтения: {err}')
    exit()

print('Подключаемся к БД.')
try:
    conn = psycopg2.connect(
        dbname="itmo_labs",
        user="postgres",
        password="OuuOuuOiuyt",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    print('Пишем в users.')
    for user in users:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, registration_date) VALUES (%s, %s, %s, %s)",
            (user['name'], user['email'], user['password_hash'], user['registration_date'])
        )
    print('Пишем в calendars.')
    for calendar in calendars:
        cursor.execute(
            "INSERT INTO calendars (title, description, created_at) VALUES (%s, %s, %s)",
            (calendar['title'], calendar['description'], calendar['created_at'])
        )

    print('Пишем в events.')
    for event in events:
        cursor.execute(
            "INSERT INTO events (title, event_date, event_time, duration, recurrence, location) VALUES (%s, %s, %s, %s, %s, %s)",
            (event['title'], event['event_date'], event['event_time'], event.get('duration', None), event.get('recurrence', None), event['location'])
        )

    conn.commit()
    print("Загрузил в таблицу.")

except Exception as err:
    print(f"Произошла ошибка: {err}")

finally:
    if conn:
        cursor.close()
        conn.close()

print('Всё.')
