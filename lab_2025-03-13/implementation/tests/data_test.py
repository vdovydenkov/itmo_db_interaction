import psycopg2

# Подключение к БД
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

# Функция для вывода записей из таблицы
def fetch_and_print_records(cursor, table_name, limit=5):
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        records = cursor.fetchall()
        print(f"Записи из таблицы {table_name}:")
        for record in records:
            print(record)
    except Exception as e:
        print(f"Ошибка при получении данных из таблицы {table_name}: {e}")

# Основная функция для тестирования
def test_database_records():
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            # Проверка и вывод записей из таблицы users
            fetch_and_print_records(cursor, "users")
            # Проверка и вывод записей из таблицы calendars
            fetch_and_print_records(cursor, "calendars")
            # Проверка и вывод записей из таблицы events
            fetch_and_print_records(cursor, "events")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        finally:
            cursor.close()
            conn.close()

# Запуск теста
test_database_records()
