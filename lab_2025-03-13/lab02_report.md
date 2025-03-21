﻿# Взаимодействие с базами данных

## Отчет по лабораторной работе №2

**Довыденков Владимир (P4150)**

13.03.2025

## Задание

1.  Из описания предметной области, полученной в ходе выполнения ЛР 1, выделить сущности, их атрибуты и связи, отразить их в инфологической модели (она же концептуальная)
2.  Составить даталогическую (она же ER-диаграмма, она же диаграмма сущность-связь) модель. При описании типов данных для атрибутов должны использоваться типы из СУБД PostgreSQL.
3.  Реализовать даталогическую модель в PostgreSQL. При описании и реализации даталогической модели должны учитываться ограничения целостности, которые характерны для полученной предметной области
4.  Заполнить созданные таблицы тестовыми данными.

## Описание предметной области

**Назначение**
Программа дает возможность пользователям управлять делами и событиями через добавление, удаление и изменение записей в календарях; помогает организовывать личное и рабочее время и согласовывать совместные дела с другими пользователями.

**Базовая функциональность**
Возможность регистрировать и удалять учетные записи пользователя. Зарегистрированный пользователь может создавать, удалять и управлять несколькими календарями. Может добавлять, редактировать, удалять записи в календарь. Может приглашать другого пользователя для совместного взаимодействия с календарем или конкретной записью.

## Сущности

**Пользователь**: информация о пользователе, включая авторизационные данные.
**Календарь**: название и описание.
**Событие**: название события, дата и время проведения, локация, сведения о продолжительности и периодичности.
**Доступ**: связывает пользователя с календарем, одновременно устанавливая права доступа пользователя к календарю.

### Пользователи (стержневая)

**Атрибуты**:
- идентификатор: первичный ключ, уникальный, обязательный;
- имя: текстовый, обязательный;
- email: верифицированный, используется для авторизации, бобязательный;
- пароль: 32 символов, хеш пароля, обязательный;
- дата регистрации: дата и время, обязательный.

### Календари (стержневая)

**Атрибуты**:
- идентификатор: первичный ключ, уникальный, обязательный;
- название: текстовый, обязательный;
- описание: текстовый, необязательный;
- дата создания: дата и время, обязательный.

### События (стержневая)

**Атрибуты**:
- идентификатор: первичный ключ, уникальный, обязательный;
- название: текстовый, обязательный;
- дата: дата, обязательный;
- время: время, необязательный;
- продолжительность: время, необязательный;
- периодичность: числовой (количество дней), необязательный;
- локация: текстовый, необязательный.

### Доступ (ассоциативная)

**Атрибуты**:
- идентификатор пользователя: внешний ключ идентификатор пользователя;
- идентификатор календаря: внешний ключ идентификатор календаря;
- доступ: числовой (от 0 до 3), обязательный.

## Связи

### Пользователь -> Календарь

Пользователь может создавать до 256 собственных календарей и быть приглашенным участником неограниченного количества календарей.
Календарь может принадлежать одному пользователю, но может быть использован неограниченным количеством других пользователей.
За связь календаря и пользователя отвечает сущность "Доступ".

### Календарь -> Событие

Календарю может принадлежать любое количество событий. Событие может принадлежать одному единственному календарю.

## Даталогическая модель

Пользователи
---------------------
- id: SERIAL PRIMARY KEY
- name: VARCHAR(100) NOT NULL
- email: VARCHAR(255) UNIQUE NOT NULL
- password_hash: CHAR(32) NOT NULL
- registration_date: TIMESTAMP NOT NULL

Календари
---------------------
- id: SERIAL PRIMARY KEY
- title: VARCHAR(100) NOT NULL
- description: TEXT
- created_at: TIMESTAMP NOT NULL

События
---------------------
- id: SERIAL PRIMARY KEY
- title: VARCHAR(100) NOT NULL
- event_date: DATE NOT NULL
- event_time: TIME
- duration: INTERVAL
- recurrence: INTEGER
- location: VARCHAR(255)

Доступ
---------------------
- user_id: INTEGER REFERENCES Пользователи(id)
- calendar_id: INTEGER REFERENCES Календари(id)
- access_level: SMALLINT CHECK (access_level BETWEEN 0 AND 3)
- PRIMARY KEY (user_id, calendar_id)

## реализация даталогической модели на SQL

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash CHAR(32) NOT NULL,
    registration_date TIMESTAMP NOT NULL
);

CREATE TABLE Calendars (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE Events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME,
    duration INTERVAL,
    recurrence INTEGER,
    location VARCHAR(255)
);

CREATE TABLE UserAccess (
    user_id INTEGER REFERENCES Users(id),
    calendar_id INTEGER REFERENCES Calendars(id),
    access_level SMALLINT CHECK (access_level BETWEEN 0 AND 3),
    PRIMARY KEY (user_id, calendar_id)
);

CREATE TABLE Calendar_Event (
    calendar_id INTEGER REFERENCES Calendars(id),
    event_id INTEGER REFERENCES Events(id),
    PRIMARY KEY (calendar_id, event_id)
);

## Выводы

В результате выполненной работы созданы таблицы Users, Calendars, Events, UserAccess и Calendar_Event.
Таблицы Users, Calendars, Events реализуют стержневые сущности, а таблицы UserAccess и Calendar_Event - ассоциативные.
Таблицы заполнены тестовыми данными.

