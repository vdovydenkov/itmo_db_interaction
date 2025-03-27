import psycopg2

try:
    conn = psycopg2.connect(
        dbname="itmo_labs",
        user="postgres",
        password="OuuOuuOiuyt",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    
    # Очистка таблиц каскадно
    tables = ["calendars", "users", "events", "useraccess", "calendar_event"]
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")
    
    # Подтверждение изменений
    conn.commit()
    print("Таблицы успешно очищены каскадно.")

except Exception as e:
    print(f"Произошла ошибка: {e}")

finally:
    if conn:
        cursor.close()
        conn.close()
