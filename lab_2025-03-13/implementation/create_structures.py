import psycopg2

# Подключение к PostgreSQL
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="OuuOuuOiuyt",
    host="localhost",
    port="5432"
)
conn.autocommit = True

# Создание курсора
cur = conn.cursor()

# Создание базы данных
cur.execute("CREATE DATABASE itmo_labs")

# Подключение к новой базе данных
conn.close()
conn = psycopg2.connect(
    dbname="itmo_labs",
    user="postgres",
    password="OuuOuuOiuyt",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Создание таблиц
cur.execute("""
    CREATE TABLE Users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash CHAR(32) NOT NULL,
        registration_date TIMESTAMP NOT NULL
    )
""")

cur.execute("""
    CREATE TABLE Calendars (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        description TEXT,
        created_at TIMESTAMP NOT NULL
    )
""")

cur.execute("""
    CREATE TABLE Events (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        event_date DATE NOT NULL,
        event_time TIME,
        duration INTERVAL,
        recurrence INTEGER,
        location VARCHAR(255)
    )
""")

cur.execute("""
    CREATE TABLE UserAccess (
        user_id INTEGER REFERENCES Users(id),
        calendar_id INTEGER REFERENCES Calendars(id),
        access_level SMALLINT CHECK (access_level BETWEEN 0 AND 3),
        PRIMARY KEY (user_id, calendar_id)
    )
""")

cur.execute("""
    CREATE TABLE Calendar_Event (
        calendar_id INTEGER REFERENCES Calendars(id),
        event_id INTEGER REFERENCES Events(id),
        PRIMARY KEY (calendar_id, event_id)
    )
""")

# Закрытие соединения
cur.close()
conn.close()