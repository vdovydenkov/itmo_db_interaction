import psycopg2

# Подключение к БД
conn = psycopg2.connect(
    dbname="itmo_labs",
    user="postgres",
    password="OuuOuuOiuyt",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Проверка существования таблиц
tables = ["Users", "Calendars", "Events", "UserAccess", "Calendar_Event"]
for table in tables:
    cur.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table.lower()}');")
    exists = cur.fetchone()[0]
    if exists:
        print(f"Таблица {table} существует.")
    else:
        print(f"Таблица {table} не найдена.")
cur.close()

conn.close()
