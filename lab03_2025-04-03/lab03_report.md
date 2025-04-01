# Взаимодействие с базами данных

## Отчет по лабораторной работе №3

**Довыденков Владимир (P4150)**

21.03.2025

## Задание

1. Реализованную в рамках лабораторной работы №2 даталогическую модель привести в 3 нормальную форму. Обосновать выбор денормализованной модели.
2. Привести 3 примера анализа функциональной зависимости атрибутов.
3. Обеспечить целостность данных таблиц при помощи средств языка DDL.
4. Заполнить таблицы данными.
5. Разработать скрипты-примеры для создания/удаления требуемых объектов базы данных, заполнения/удаления содержимого созданных таблиц.
6. Составить 6+3 примеров SQL запросов на объединение таблиц предметной области: INNER, FULL, LEFT, RIGTH, CROSS, OUTER; JOIN ON, JOIN USING, NATURAL JOIN.

## Описание предметной области

**Назначение**
Программа дает возможность пользователям управлять делами и событиями через добавление, удаление и изменение записей в календарях; помогает организовывать личное и рабочее время и согласовывать совместные дела с другими пользователями.

**Базовая функциональность**
Возможность регистрировать и удалять учетные записи пользователя. Зарегистрированный пользователь может создавать, удалять и управлять несколькими календарями. Может добавлять, редактировать, удалять записи в календарь. Может приглашать другого пользователя для совместного взаимодействия с календарем или конкретной записью.

## Даталогическая модель

@startuml

entity "Users" {
  + id: SERIAL PRIMARY KEY
  --
  name: VARCHAR(100) NOT NULL
  email: VARCHAR(255) UNIQUE NOT NULL
  password_hash: BYTEA NOT NULL
  registration_date: TIMESTAMP NOT NULL
}

entity "Calendars" {
  + id: SERIAL PRIMARY KEY
  --
  title: VARCHAR(100) NOT NULL
  description: TEXT
  created_at: TIMESTAMP NOT NULL
}

entity "Events" {
  + id: SERIAL PRIMARY KEY
  --
  title: VARCHAR(100) NOT NULL
  event_date: DATE NOT NULL
  event_time: TIME
  duration: INTERVAL
  recurrence: INTEGER
  location: VARCHAR(255)
}

entity "UserAccess" {
  + user_id: INTEGER
  + calendar_id: INTEGER
  --
  access_level: SMALLINT CHECK (access_level BETWEEN 0 AND 3)
  PRIMARY KEY (user_id, calendar_id)
}

entity "Calendar_Event" {
  + calendar_id: INTEGER
  + event_id: INTEGER
  --
  PRIMARY KEY (calendar_id, event_id)
}

Users ||--o{ UserAccess : "1"
Calendars ||--o{ UserAccess : "1..*"
Calendars ||--o{ Calendar_Event : "1"
Events ||--o{ Calendar_Event : "1..*"

@enduml

## Анализ функциональной зависимости

### Таблица "Пользователи"
- **Функциональные зависимости**:
  - `id` → `name`, `email`, `password_hash`, `registration_date`
  - `email` → `id`, `name`, `password_hash`, `registration_date` (поскольку `email` уникален, он также может служить ключом)
- **Ключи**:
  - Первичный ключ: `id`
  - Кандидат на ключ: `email`

### Таблица "Календари"
- **Функциональные зависимости**:
  - `id` → `title`, `description`, `created_at`
- **Ключи**:
  - Первичный ключ: `id`

### Таблица "События"
- **Функциональные зависимости**:
  - `id` → `title`, `event_date`, `event_time`, `duration`, `recurrence`, `location`
- **Ключи**:
  - Первичный ключ: `id`

## Примеры SQL-запросов на заполнения данными

**Добавление пользователя**

INSERT INTO users (name, email, password_hash, registration_date)
    VALUES ('Дормидонт Валерьевич', 'dormik@fakemail.zoo', hashed_password, NOW());

**Добавление календаря**

WITH new_calendar AS (
    INSERT INTO Calendars (title, description, created_at)
    VALUES ('Досуг', 'События для отдохновения души!', NOW())
    RETURNING id
)

INSERT INTO UserAccess (user_id, calendar_id, access_level)
VALUES (
    (SELECT id FROM Users WHERE name = 'Дормидонт Валерьевич'),
    (SELECT id FROM new_calendar),
    0
);

**Добавление события**

WITH new_event AS (
    INSERT INTO Events (title, event_date, event_time, duration, location)
    VALUES ('Концерт', '2025-03-28', '19:00:00', '2 hours 30 minutes', 'Концертный зал Мариинского театра.')
    RETURNING id
)

INSERT INTO Calendar_Event (calendar_id, event_id)
VALUES (
    (SELECT id FROM Calendars WHERE title = 'Досуг'),
    (SELECT id FROM new_event)
);

## Примеры SQL-запросов на объединение таблиц

**Объединяем пользователей с пренадлежащими им календарями и с уровнем доступа.**

SELECT Users.name, Calendars.title, UserAccess.access_level
FROM Users
INNER JOIN UserAccess ON UserAccess.user_id = Users.id
INNER JOIN Calendars ON UserAccess.calendar_id = Calendars.id;

**Показать пользователей и календари, включая пользователей, у которых нет календарей.**

SELECT Users.name, Calendars.title, UserAccess.access_level 
FROM Users 
FULL JOIN UserAccess ON Users.id = UserAccess.user_id 
LEFT JOIN Calendars ON UserAccess.calendar_id = Calendars.id;

**То же самое с "RIGHT JOIN".**

SELECT Calendars.title, Users.name
FROM Calendars
RIGHT JOIN UserAccess ON Calendars.id = UserAccess.calendar_id
RIGHT JOIN Users ON UserAccess.user_id = Users.id;

**Все возможные пары пользователей и календарей, независимо от того, есть ли у пользователя доступ к календарю.**

SELECT Users.name, Calendars.title 
FROM Users 
CROSS JOIN Calendars;

**Действующие примеры с JOIN ... USING и NATURAL JOIN на этом наборе таблиц выполнить невозможно, так как отсутствуют столбцы с одинаковыми названиями, совпадающие по значению.**

