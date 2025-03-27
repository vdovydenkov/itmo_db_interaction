## Описание задания

Тема: Межгалактическое зоосопровождение
Описание: Ваша задача — создать систему для отслеживания и управления сущностями из различных уголков вселенной, обеспечивая учет их сред обитания, особенностей и планирования перемещений.

1. составить даталогическую модель
2. составить запросы на создание таблиц и вставку данных

## Сущности

Существа - стержневая сущность.
Атрибуты:
- идентификатор (уникальный)
- Название: имя существа;
- Комментарии: индивидуальные особенности, потребности... Заболевания и пр.

Локация - стержневая
- идентификатор: уникальный;
- название: наименование локации;
- координаты: пространственные координаты локации;

Среда обитания - стержневая сущность.
- идентификатор: уникальный;
- название: название среды обитания;
- атмосфера: характеристики атмосферы;
- тяготение: сила тяжести;
- характеристика среды: водная, воздушная, поверхностная, подземная;
- химический состав: описание химического состава среды.

## Связи

Существо_Локация
Существо -> локация : образуют связь "Один ко многим". 

Журнал_перемещений
Атрибуты:
- идентификатор существа
- идентификатор локации;
- дата прибытия (null, если исходная локация)
- дата убытия (NULL - если это текущая локация).

Локация_СредаОбитания
- Идентификатор локации;
- идентификатор среды обитания.

## Реализация

CREATE TABLE CREATURES (
    id SERIAL PRIMARY KEY,
    title VARCHAR[100] NOT NULL,
    comments TEXT
);

CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    coordinates NUMERIC[],
);

CREATE TABLE habitats (
    id SERIAL PRIMARY KEY,
    TITLE varchar(100) NT NULL,
    atmosphere VARCHAR(512) NOT NULL,
    gravity NUMERIC NOT NULL,
    environment VARCHAR(50) NOT NULL,
    chemical_composition TEXT
);

CREATE TABLE Creature_Location (
    creature_id INTEGER REFERENCES creatures(id),
    location_id INTEGER REFERENCES Locations(id),
    PRIMARY KEY (Creature_id, Location_id)
);

CREATE TABLE Movement_Log (
    creature_id INTEGER REFERENCES creatures(id),
    location_id INTEGER REFERENCES Locations(id),
    arrival_date TIMESTAMP,
    departure_date TIMESTAMP
    PRIMARY KEY (Creature_id, Location_id)
);

CREATE TABLE Location_Habitat (
    Location_id INTEGER REFERENCE Locations(id),
    habitat INTEGER REFERENCES habitat(id)
    PRIMARY KEY (location_id, habitat_id)
);


## Добавление данных

Creatures 
INSERT INTO creature (title, comments) VALUES ("Порторус гребенчетохвостый", "Внимание! Со спины не заходить, может лягнуть!");

 Locations 
INSERT INTO Locations (title, coordinates) VALUES ("Азигорус Веги", ARRAY[128744.463, 126350863.221, 327861.3647]);

Habitats 
INSERT INTO Habitats (title, atmosphere, gravity, environment, chemical_composition) VALUES ("Кислотное море", "Азот 23%, кислород 4%", 8, "жидкая", "Серная кислота 10%");


