import psycopg2
import hashlib
    
DB_CONFIG = {
    "dbname": "itmo_labs",
    "user": "postgres",
    "password": "OuuOuuOiuyt",
    "host": "localhost",
    "port": "5432",
}

def hash_password(password):
    # Создаем объект хеша
    hash_object = hashlib.sha256()
    # Обновляем объект хеша строкой пароля, преобразованной в байты
    hash_object.update(password.encode('utf-8'))
    # Возвращаем хеш
    return hash_object.digest()

def connect_db():
    print('Подключаюсь к БД.')
    try:
        conn = psycopg2.connect(**DB_CONFIG)
    except Exception as err_message:
        print('Ошибка: ', err_message)
        exit()
    return conn

def show_users():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM users;")
            users = cur.fetchall()
            if not users:
                print("Нет пользователей.")
                return []
            print("Пользователи:")
            for idx, u in enumerate(users, 1):
                print(f"{idx}. {u[1]} ({u[2]})")
            return users

def show_calendars():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title FROM Calendars;")
            calendars = cur.fetchall()
            if not calendars:
                print("Нет календарей.")
                return []
            print("Календари:")
            for idx, c in enumerate(calendars, 1):
                print(f"{idx}. {c[1]}")
            return calendars

def show_events(calendar_id=None):
    with connect_db() as conn:
        with conn.cursor() as cur:
            if calendar_id:
                cur.execute("SELECT id, title FROM Events WHERE id IN (SELECT event_id FROM Calendar_Event WHERE calendar_id = %s);", (calendar_id,))
            else:
                cur.execute("SELECT id, title FROM Events;")
            events = cur.fetchall()
            if not events:
                print("Нет событий.")
                return []
            print("События:")
            for idx, e in enumerate(events, 1):
                print(f"{idx}. {e[1]}")
            return events

def add_user():
    name = input("Имя: ")
    email = input("Почта: ")
    password = input("Пароль: ")
    hashed_password = hash_password(password)
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (name, email, password_hash, registration_date) VALUES (%s, %s, %s, NOW());", (name, email, hashed_password))
            conn.commit()
            print(f"Пользователь {name} добавлен.")

def add_calendar():
    users = show_users()
    if not users:
        return
    user_idx = int(input("Выберите номер пользователя: ")) - 1
    if user_idx < 0 or user_idx >= len(users):
        print('Такого номера нет.')
        return
    user_id = users[user_idx][0]

    title = input("Название календаря: ")
    description = input("Описание: ")
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO Calendars (title, description, created_at) VALUES (%s, %s, NOW()) RETURNING id;", (title, description))
            calendar_id = cur.fetchone()[0]
            cur.execute("INSERT INTO UserAccess (user_id, calendar_id, access_level) VALUES (%s, %s, 0);", (user_id, calendar_id))
            conn.commit()
            print(f"Календарь '{title}' создан.")

def add_event():
    calendars = show_calendars()
    if not calendars:
        return
    calendar_idx = int(input("Выберите номер календаря: ")) - 1
    if calendar_idx < 0 or calendar_idx >= len(calendars):
        print('Такого номера нет.')
        return
    calendar_id = calendars[calendar_idx][0]

    title = input("Название события: ")
    event_date = input("Дата события (ГГГГ-ММ-ДД): ")
    event_time = input("Время события (ЧЧ:ММ, можно оставить пустым): ") or None
    duration = input("Продолжительность (например, '1 hour', можно оставить пустым): ") or None
    location = input("Место события (можно оставить пустым): ") or None

    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO Events (title, event_date, event_time, duration, location) VALUES (%s, %s, %s, %s, %s) RETURNING id;", 
                        (title, event_date, event_time, duration, location))
            event_id = cur.fetchone()[0]
            cur.execute("INSERT INTO Calendar_Event (calendar_id, event_id) VALUES (%s, %s);", (calendar_id, event_id))
            conn.commit()
            print(f"Событие '{title}' добавлено.")

def delete_user():
    users = show_users()
    if not users:
        return
    user_idx = int(input("Выберите номер пользователя: ")) - 1
    if user_idx < 0 or user_idx >= len(users):
        print('Такого номера нет.')
        return
    user_id = users[user_idx][0]

    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM UserAccess WHERE user_id = %s;", (user_id,))
            cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))
            conn.commit()
            print(f"Пользователь {users[user_idx][1]} удалён.")

def delete_calendar():
    calendars = show_calendars()
    if not calendars:
        return
    calendar_idx = int(input("Выберите номер календаря: ")) - 1
    if calendar_idx < 0 or calendar_idx >= len(calendars):
        print('Такого номера нет.')
        return
    calendar_id = calendars[calendar_idx][0]

    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM UserAccess WHERE calendar_id = %s;", (calendar_id,))
            cur.execute("DELETE FROM Calendar_Event WHERE calendar_id = %s;", (calendar_id,))
            cur.execute("DELETE FROM Calendars WHERE id = %s;", (calendar_id,))
            conn.commit()
            print(f"Календарь {calendars[calendar_idx][1]} удалён.")

def delete_event():
    calendars = show_calendars()
    if not calendars:
        return
    calendar_idx = int(input("Выберите номер календаря: ")) - 1
    if calendar_idx < 0 or calendar_idx >= len(calendars):
        print('Такого номера нет.')
        return
    calendar_id = calendars[calendar_idx][0]

    events = show_events(calendar_id)
    if not events:
        return
    event_idx = int(input("Выберите номер события: ")) - 1
    if event_idx < 0 or event_idx >= len(events):
        print('Такого номера нет.')
        return
    event_id = events[event_idx][0]

    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Calendar_Event WHERE event_id = %s;", (event_id,))
            cur.execute("DELETE FROM Events WHERE id = %s;", (event_id,))
            conn.commit()
            print(f"Событие {events[event_idx][1]} удалено.")

while True:
    print("\nМеню:")
    print("1. Показать")
    print("2. Добавить")
    print("3. Удалить")
    print("0. Выйти")

    choice = input("Выберите действие: ")
    if choice == "1":
        print("\n1.1. Пользователей")
        print("1.2. Календари")
        print("1.3. События")
        sub_choice = input("Выберите действие: ")
        if sub_choice == "1":
            show_users()
        elif sub_choice == "2":
            show_calendars()
        elif sub_choice == "3":
            show_events()
    elif choice == "2":
        print("\n2.1. Добавить пользователя")
        print("2.2. Добавить календарь")
        print("2.3. Добавить событие")
        sub_choice = input("Выберите действие: ")
        if sub_choice == "1":
            add_user()
        elif sub_choice == "2":
            add_calendar()
        elif sub_choice == "3":
            add_event()
    elif choice == "3":
        print("\n3.1. Удалить пользователя")
        print("3.2. Удалить календарь")
        print("3.3. Удалить событие")
        sub_choice = input("Выберите действие: ")
        if sub_choice == "1":
            delete_user()
        elif sub_choice == "2":
            delete_calendar()
        elif sub_choice == "3":
            delete_event()
    elif choice == "0":
        print("Выход из программы.")
        break

