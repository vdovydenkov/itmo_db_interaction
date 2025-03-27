import psycopg2

# Подключение к базе данных PostgreSQL
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="itmo_labs",
            user="postgres",
            password="OuuOuuOiuyt",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

def link_calendars_to_users():
    conn = connect_to_db()
    cur = conn.cursor()

    # Извлекаем всех пользователей и календари
    cur.execute("SELECT id FROM users")
    users = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT id FROM Calendars")
    calendars = [row[0] for row in cur.fetchall()]

    # Связываем календари с пользователями
    user_count = len(users)
    user_index = 0

    for calendar_id in calendars:
        user_id = users[user_index]
        cur.execute(
            "INSERT INTO UserAccess (user_id, calendar_id, access_level) VALUES (%s, %s, %s)",
            (user_id, calendar_id, 0)
        )
        user_index = (user_index + 1) % user_count

    conn.commit()
    cur.close()
    conn.close()

def link_events_to_calendars():
    conn = connect_to_db()
    cur = conn.cursor()

    # Извлекаем все события и календари
    cur.execute("SELECT id FROM Events")
    events = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT id FROM Calendars")
    calendars = [row[0] for row in cur.fetchall()]

    # Связываем события с календарями
    calendar_count = len(calendars)
    calendar_index = 0

    for event_id in events:
        calendar_id = calendars[calendar_index]
        cur.execute(
            "INSERT INTO Calendar_Event (calendar_id, event_id) VALUES (%s, %s)",
            (calendar_id, event_id)
        )
        calendar_index = (calendar_index + 1) % calendar_count

    conn.commit()
    cur.close()
    conn.close()

link_calendars_to_users()
link_events_to_calendars()
