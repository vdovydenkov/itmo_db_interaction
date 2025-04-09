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
- События в одном календаре не могут пересекаться по времени. Если новое событие пересекается с уже существующим, оно не должно добавляться.
- Событие не может начинаться в прошлом.
- Если у события указана "периодичность", то также обязательно должны быть заполнены дата и время начала. В противном случае — ошибка при создании или обновлении записи.
**Изменение доступа к календарю**  
- При изменении владельца (например, если текущий владелец удаляется), должен назначаться новый владелец.
- - Если пользователь является владельцем хотя бы одного календаря, он не может быть удален до передачи прав или удаления календарей.
**Удаление записей.**
- При удалении календаря должны удаляться связанные записи в `UserAccess` и `Calendar_Event`.
- При удалении события оно должно удаляться из всех связей с календарями.

### ТРИГГЕРЫ

1. **Ограничение: не более 256 календарей на пользователя**

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

2. **Запрет пересекающихся событий в одном календаре**

CREATE FUNCTION prevent_event_overlap() RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM Calendar_Event ce1
        JOIN Events e1 ON ce1.event_id = e1.id
        WHERE ce1.calendar_id IN (
            SELECT calendar_id FROM Calendar_Event WHERE event_id = NEW.id
        )
        AND e1.event_date = NEW.event_date
        AND e1.id != NEW.id
        AND (
            tstzrange(e1.event_time, e1.event_time + COALESCE(e1.duration, INTERVAL '0')) &&
            tstzrange(NEW.event_time, NEW.event_time + COALESCE(NEW.duration, INTERVAL '0'))
        )
    ) THEN
        RAISE EXCEPTION 'Событие пересекается с другим в этом календаре.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_event_overlap
BEFORE INSERT OR UPDATE ON Events
FOR EACH ROW
EXECUTE FUNCTION prevent_event_overlap();

---

3. **Событие не может начинаться в прошлом**

CREATE FUNCTION prevent_past_event() RETURNS TRIGGER AS $$
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

4. **Если есть периодичность — дата и время обязательны**

CREATE FUNCTION validate_recurring_event() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.recurrence IS NOT NULL THEN
        IF NEW.event_date IS NULL OR NEW.event_time IS NULL THEN
            RAISE EXCEPTION 'Для повторяющегося события необходимо указать дату и время начала.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_recurring_event
BEFORE INSERT OR UPDATE ON Events
FOR EACH ROW
EXECUTE FUNCTION validate_recurring_event();

---

5. **Запрет удаления пользователя с правами владельца**

CREATE FUNCTION prevent_owner_deletion() RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM UserAccess
        WHERE user_id = OLD.id AND access_level = 3
    ) THEN
        RAISE EXCEPTION 'Нельзя удалить пользователя, пока он владеет хотя бы одним календарем.';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_owner_deletion
BEFORE DELETE ON Users
FOR EACH ROW
EXECUTE FUNCTION prevent_owner_deletion();

---

### Процедуры и функции

1. **Удаление календаря и связанных записей**

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

2. **Удаление события и связей**

CREATE PROCEDURE delete_event_with_links(IN ev_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM Calendar_Event WHERE event_id = ev_id;
    DELETE FROM Events WHERE id = ev_id;
END;
$$;

---

3. **Назначение нового владельца при удалении текущего**

CREATE PROCEDURE transfer_calendar_ownership(IN old_owner_id INTEGER, IN target_calendar_id INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    new_owner_id INTEGER;
BEGIN
    -- Поиск нового пользователя, у которого есть доступ, кроме текущего владельца
    SELECT user_id INTO new_owner_id
    FROM UserAccess
    WHERE calendar_id = target_calendar_id AND user_id != old_owner_id
    ORDER BY access_level DESC
    LIMIT 1;

    IF new_owner_id IS NULL THEN
        RAISE EXCEPTION 'Невозможно назначить нового владельца — других пользователей нет.';
    END IF;

    -- Назначение нового владельца
    UPDATE UserAccess
    SET access_level = 3
    WHERE user_id = new_owner_id AND calendar_id = target_calendar_id;

    -- Удаление старого владельца
    DELETE FROM UserAccess
    WHERE user_id = old_owner_id AND calendar_id = target_calendar_id;
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

