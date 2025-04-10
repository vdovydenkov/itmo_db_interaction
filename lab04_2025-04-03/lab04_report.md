# Взаимодействие с базами данных

## Отчет по лабораторной работе №4

**Довыденков Владимир (P4150)**

03.04.2025

## Задание

Для выполнения лабораторной работы необходимо:
·  Описать бизнес-правила вашей предметной области. Какие в вашей системе могут быть действия, требующие выполнения запроса в БД. Эти бизнес-правила будут использованы для реализации триггеров, функций, процедур, транзакций поэтому приниматься будут только достаточно интересные бизнес-правила
·  Добавить в ранее созданную базу данных триггеры для обеспечения комплексных ограничений целостности. Триггеров должно быть не менее трех
·  Реализовать функции и процедуры на основе описания бизнес-процессов, определенных при описании предметной области из пункта 1. Примеров не менее 3
·  Привести 3 примера выполнения транзакции. Это может быть, например, проверка корректности вводимых данных для созданных функций и процедур. Например, функция, которая вносит данные. Данные проверяются и в случае если они не подходят ограничениям целостности, транзакция должна откатываться
·  Необходимо произвести анализ использования созданной базы данных, выявить наиболее часто используемые объекты базы данных, виды запросов к ним. Результаты должны быть представлены в виде текстового описания
·  На основании полученного описания требуется создать подходящие индексы и доказать, что они будут полезны для представленных в описании случаев использования базы данных.

### Бизнес-правила предметной области

**Ограничение количества календарей на пользователя**  
- Пользователь может создать не более 256 собственных календарей. Нарушение этого правила должно вызывать ошибку.
**Ограничение на события в одном календаре**  
- Событие не может начинаться в прошлом.
- Если у события указана "продолжительность", то также обязательно должно быть указано время начала. В противном случае — ошибка при создании или обновлении записи.
**Изменение доступа к календарю**  
- При изменении владельца (например, если текущий владелец удаляется), должен назначаться новый владелец на все "несвободные".
- Если пользователь является владельцем хотя бы одного календаря, он не может быть удален до передачи прав или удаления календарей.
**Удаление записей.**
- При удалении календаря должны удаляться связанные записи в `UserAccess` и `Calendar_Event`.
- При удалении события оно должно удаляться из всех связей с календарями.

### ТРИГГЕРЫ

**1. Ограничение: не более 256 календарей на пользователя.**

CREATE FUNCTION check_calendar_limit()
RETURNS TRIGGER AS $$
DECLARE
  calendar_count INT;
BEGIN
  SELECT COUNT(*) INTO calendar_count FROM UserAccess
  WHERE user_id = NEW.user_id AND access_level = 3;

  IF calendar_count >= 256 THEN
    RAISE EXCEPTION 'Пользователь достиг лимита в 256 календарей';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_calendar_limit
BEFORE INSERT ON UserAccess
FOR EACH ROW
WHEN (NEW.access_level = 3)
EXECUTE FUNCTION check_calendar_limit();

---

**2. Событие не может начинаться в прошлом.**

CREATE FUNCTION prevent_past_event()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.event_date < CURRENT_DATE OR
       (NEW.event_date = CURRENT_DATE AND NEW.event_time < CURRENT_TIME) THEN
        RAISE EXCEPTION 'Нельзя создавать события в прошлом.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_past_event
BEFORE INSERT OR UPDATE ON Events
FOR EACH ROW
EXECUTE FUNCTION prevent_past_event();

---

**3. Если есть продолжительность — время начала события обязательно.**

CREATE FUNCTION validate_during_event()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.duration IS NOT NULL AND NEW.event_time IS NULL THEN
        RAISE EXCEPTION 'Для длящегося события необходимо указать время начала.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_recurring_event
BEFORE INSERT OR UPDATE ON Events
FOR EACH ROW
EXECUTE FUNCTION validate_during_event();

---

### Процедуры и функции

**1. Удаление календаря и связанных записей.**

CREATE PROCEDURE delete_calendar_with_links(IN cal_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM Calendar_Event WHERE calendar_id = cal_id;
    DELETE FROM UserAccess WHERE calendar_id = cal_id;
    DELETE FROM Calendars WHERE id = cal_id;
END;
$$;

---

**2. Удаление события и связей.**

CREATE PROCEDURE delete_event_with_links(IN ev_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM Calendar_Event WHERE event_id = ev_id;
    DELETE FROM Events WHERE id = ev_id;
END;
$$;

---

**3. Принудительное переназначение владельцев календарей.**

CREATE PROCEDURE transfer_calendars(IN owner_id INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    target_calendar_id INTEGER;
    new_owner_id INTEGER;
BEGIN
    -- Цикл по всем календарям, где пользователь является владельцем
    FOR target_calendar_id IN
        SELECT DISTINCT calendar_id
        FROM UserAccess
        WHERE user_id = owner_id AND access_level = 3
    LOOP
        -- Поиск нового пользователя, у которого есть доступ, кроме текущего владельца
        SELECT user_id INTO new_owner_id
        FROM UserAccess
        WHERE calendar_id = target_calendar_id
            AND user_id != owner_id
            AND access_level < 3
        ORDER BY access_level DESC, user_id
        LIMIT 1;

        IF new_owner_id IS NOT NULL THEN
            -- Назначение нового владельца
            UPDATE UserAccess
            SET access_level = 3
            WHERE user_id = new_owner_id AND calendar_id = target_calendar_id;

            -- Удаление связи со старым владельцем
            DELETE FROM UserAccess
            WHERE user_id = owner_id AND calendar_id = target_calendar_id;
        END IF;
    END LOOP;
END;
$$;

---

### Транзакции

**Трансформированная в транзакцию версия процедуры удаления календаря.**

CREATE PROCEDURE transactional_delete_calendar(IN cal_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    BEGIN
        -- Старт транзакции
        DELETE FROM Calendar_Event WHERE calendar_id = cal_id;
        DELETE FROM UserAccess WHERE calendar_id = cal_id;
        DELETE FROM Calendars WHERE id = cal_id;
        -- Коммит происходит автоматически при завершении процедуры без ошибок
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Ошибка при удалении календаря: %', SQLERRM;
            RAISE;
    END;
END;
$$;


### Анализ использования базы данных

**Нагруженность сущностей:**
1. **Users** – при логине, регистрации, отображении профиля, проверке доступа.
2. **Calendars** – при просмотре, создании, редактировании календарей.
3. **Events** – основная сущность взаимодействия, особенно при отображении событий на определённую дату.
4. **UserAccess** – при проверке прав доступа, отображении совместных календарей.
5. **Calendar_Event** – при связке событий с календарями (чтение/удаление/поиск пересечений).

**Основные типы запросов:**
- **SELECT с фильтрацией по дате** (Events)
- **JOIN для связи Events с Calendar_Event и Calendars**
- **JOIN Users с UserAccess для проверки уровня доступа**

У одного пользователя может быть несколько (или даже несколько десятков) календарей, а у каждого календаря несколько (или даже несколько десятков) событий. При этом "событие" — основная сущность, с которой чаще всего оперирует пользователь.
Таким образом:
1. **Events** — сущность с самым большим количеством записей из стержневых сущностей и с самым большим количеством операций.
2. **Calendar_Event** — записей и операций не меньше, чем в сущности Events, поскольку каждое событие обязательно связано с календарем. И только операции обновления могут проводиться с сущностью Events, не касаясь Calendar_Event.
3. **UserAccess** — третья по степени "нагруженности", поскольку задействуется каждый раз при проверке прав доступа пользователя к календарю.

---

### Обоснование индексов

**1. Events (event_date)**

CREATE INDEX idx_events_event_date ON Events(event_date);

**Обоснование:** частые выборки событий на определённую дату (`WHERE event_date = ?`).

**2. Calendar_Event (calendar_id)**

CREATE INDEX idx_calendar_event_calendar_id ON Calendar_Event(calendar_id);

**Обоснование:** часто используется в JOIN при выборке событий календаря.

**3. Calendar_Event (event_id)**

CREATE INDEX idx_calendar_event_event_id ON Calendar_Event(event_id);

**Обоснование:** для быстрого удаления или получения календарей по событию.

**4. UserAccess (user_id)**

CREATE INDEX idx_user_access_user_id ON UserAccess(user_id);

**Обоснование:** проверка доступа пользователя к календарям.


