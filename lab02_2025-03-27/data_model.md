## �������� �������

����: ���������������� ����������������
��������: ���� ������ � ������� ������� ��� ������������ � ���������� ���������� �� ��������� ������� ���������, ����������� ���� �� ���� ��������, ������������ � ������������ �����������.

1. ��������� �������������� ������
2. ��������� ������� �� �������� ������ � ������� ������

## ��������

�������� - ���������� ��������.
��������:
- ������������� (����������)
- ��������: ��� ��������;
- �����������: �������������� �����������, �����������... ����������� � ��.

������� - ����������
- �������������: ����������;
- ��������: ������������ �������;
- ����������: ���������������� ���������� �������;

����� �������� - ���������� ��������.
- �������������: ����������;
- ��������: �������� ����� ��������;
- ���������: �������������� ���������;
- ���������: ���� �������;
- �������������� �����: ������, ���������, �������������, ���������;
- ���������� ������: �������� ����������� ������� �����.

## �����

��������_�������
�������� -> ������� : �������� ����� "���� �� ������". 

������_�����������
��������:
- ������������� ��������
- ������������� �������;
- ���� �������� (null, ���� �������� �������)
- ���� ������ (NULL - ���� ��� ������� �������).

�������_�������������
- ������������� �������;
- ������������� ����� ��������.

## ����������

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


## ���������� ������

Creatures 
INSERT INTO creature (title, comments) VALUES ("�������� �����������������", "��������! �� ����� �� ��������, ����� �������!");

 Locations 
INSERT INTO Locations (title, coordinates) VALUES ("�������� ����", ARRAY[128744.463, 126350863.221, 327861.3647]);

Habitats 
INSERT INTO Habitats (title, atmosphere, gravity, environment, chemical_composition) VALUES ("��������� ����", "���� 23%, �������� 4%", 8, "������", "������ ������� 10%");


