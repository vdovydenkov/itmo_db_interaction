import os
import json
from faker import Faker
import random
from datetime import timedelta

file_path = os.path.dirname(os.path.abspath(__file__))
USERS_FILE_NAME = os.path.join(file_path, 'users.json')
CALENDARS_FILE_NAME = os.path.join(file_path, 'calendars.json')
EVENTS_FILE_NAME = os.path.join(file_path, 'events.json')

# Установка локали на русский язык
fake = Faker('ru_RU')

# Генерация данных для таблицы users
def generate_users(n):
    users = []
    for _ in range(n):
        user = {
            'name': fake.name(),
            'email': fake.unique.email(),
            'password_hash': fake.md5(),
            'registration_date': fake.date_time_this_decade().isoformat()
        }
        users.append(user)
    return users

# Генерация данных для таблицы calendars
def generate_calendars(n):
    calendars = []
    for _ in range(n):
        calendar = {
            'title': fake.sentence(nb_words=3),
            'description': fake.text(),
            'created_at': fake.date_time_this_year().isoformat()
        }
        calendars.append(calendar)
    return calendars

# Генерация данных для таблицы events
def generate_events(n):
    events = []
    for _ in range(n):
        event = {
            'title': fake.sentence(nb_words=3),
            'event_date': fake.date_this_year().isoformat(),
            'event_time': fake.time(),
            'duration': str(timedelta(minutes=random.randint(30, 180))),
            'recurrence': random.randint(0, 10),
            'location': fake.address()
        }
        events.append(event)
    return events

# Запись данных в JSON-файлы
def write_to_json(filename, data):
    try: # Пишем в файл
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as err:
        print(f'Ошибка при записи: {err}')

# Генерация и запись данных
users = generate_users(100)
calendars = generate_calendars(120)
events = generate_events(1500)

# Запись данных в JSON-файлы
write_to_json(USERS_FILE_NAME, users)
write_to_json(CALENDARS_FILE_NAME, calendars)
write_to_json(EVENTS_FILE_NAME, events)

print("Сделал.")

