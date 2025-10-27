#не заполненная версия

import sqlite3
from datetime import datetime

# 1. Определение SQL-запросов для создания таблиц (DDL)
CREATE_TABLES_SQL = """
-- Таблица Coach
CREATE TABLE IF NOT EXISTS Coach (
    Coach_ID_int INTEGER PRIMARY KEY,
    Internal_number_int INTEGER NOT NULL UNIQUE,
    Surname_text TEXT NOT NULL,
    Name_text TEXT NOT NULL,
    Experience_int INTEGER,
    Password_text TEXT NOT NULL
);

-- Таблица User
CREATE TABLE IF NOT EXISTS User (
    User_ID_int INTEGER PRIMARY KEY,
    Surname_text TEXT NOT NULL,
    Name_text TEXT NOT NULL,
    Password_text TEXT NOT NULL
);

-- Таблица Inventory
CREATE TABLE IF NOT EXISTS Inventory (
    Inventory_ID_int INTEGER PRIMARY KEY,
    Name_text TEXT NOT NULL,
    Number_int INTEGER,
    Comment_text TEXT
);

-- Таблица Status
CREATE TABLE IF NOT EXISTS Status (
    Status_ID_int INTEGER PRIMARY KEY,
    Name_text TEXT NOT NULL,
    Comment_text TEXT
);

-- Таблица Booking
CREATE TABLE IF NOT EXISTS Booking (
    Booking_ID_int INTEGER PRIMARY KEY,
    Coach_ID_int INTEGER NOT NULL,
    User_ID_int INTEGER NOT NULL,
    Time_start_date TEXT NOT NULL, -- Используем TEXT для хранения даты
    Time_end_date TEXT NOT NULL,   -- Используем TEXT для хранения даты
    Number_booking_int INTEGER,
    FOREIGN KEY (Coach_ID_int) REFERENCES Coach(Coach_ID_int),
    FOREIGN KEY (User_ID_int) REFERENCES User(User_ID_int)
);

-- Таблица Booking_inventory
CREATE TABLE IF NOT EXISTS Booking_inventory (
    Booking_inventory_ID_int INTEGER PRIMARY KEY,
    Inventory_ID_int INTEGER NOT NULL,
    Booking_ID_int INTEGER NOT NULL,
    Status_ID_int INTEGER NOT NULL,
    FOREIGN KEY (Inventory_ID_int) REFERENCES Inventory(Inventory_ID_int),
    FOREIGN KEY (Booking_ID_int) REFERENCES Booking(Booking_ID_int),
    FOREIGN KEY (Status_ID_int) REFERENCES Status(Status_ID_int)
);
"""

# 2. Определение данных для вставки (DML)
DATA_INSERTION_SQL = [
    ("INSERT INTO Coach (Internal_number_int, Surname_text, Name_text, Experience_int, Password_text) VALUES (?, ?, ?, ?, ?)", (101, 'Иванов', 'Петр', 5, 'coach_pass123')),
    ("INSERT INTO User (Surname_text, Name_text, Password_text) VALUES (?, ?, ?)", ('Сидоров', 'Антон', 'user_pass456')),
    ("INSERT INTO Inventory (Name_text, Number_int) VALUES (?, ?)", ('Футбольный мяч', 15)),
    ("INSERT INTO Status (Name_text) VALUES (?)", ('Забронировано')),
    ("INSERT INTO Booking (Coach_ID_int, User_ID_int, Time_start_date, Time_end_date, Number_booking_int) VALUES (?, ?, ?, ?, ?)", (1, 1, '2025-10-30', '2025-10-30', 1)),
    ("INSERT INTO Booking_inventory (Inventory_ID_int, Booking_ID_int, Status_ID_int) VALUES (?, ?, ?)", (1, 1, 1)),
]

# 3. Определение запроса для выборки данных (DQL)
SELECT_QUERY = """
SELECT
    B.Time_start_date,
    C.Name_text AS Coach_Name,
    U.Name_text AS User_Name,
    I.Name_text AS Inventory_Name,
    S.Name_text AS Booking_Status
FROM
    Booking AS B
JOIN
    Coach AS C ON B.Coach_ID_int = C.Coach_ID_int
JOIN
    User AS U ON B.User_ID_int = U.User_ID_int
JOIN
    Booking_inventory AS BI ON B.Booking_ID_int = BI.Booking_ID_int
JOIN
    Inventory AS I ON BI.Inventory_ID_int = I.Inventory_ID_int
JOIN
    Status AS S ON BI.Status_ID_int = S.Status_ID_int;
"""

def setup_database():
    """Создает подключение, таблицы и заполняет их данными."""
    print("Подключение к базе данных 'sports_booking.db'...")
    conn = sqlite3.connect('sports_booking.db')
    cursor = conn.cursor()

    try:
        # 1. Создание таблиц
        print("Создание таблиц...")
        cursor.executescript(CREATE_TABLES_SQL)
        conn.commit()
        print("Таблицы успешно созданы.")

        # 2. Вставка данных
        print("Вставка тестовых данных...")
        for sql, params in DATA_INSERTION_SQL:
            cursor.execute(sql, params)
        conn.commit()
        print("Данные успешно вставлены.")

        # 3. Выполнение SELECT-запроса
        print("\n--- Результат выполнения SELECT-запроса ---")
        cursor.execute(SELECT_QUERY)
        
        # Получение имен столбцов
        columns = [description[0] for description in cursor.description]
        print(columns)
        
        # Вывод данных
        for row in cursor.fetchall():
            print(row)
            
    except sqlite3.Error as e:
        print(f"Произошла ошибка SQLite: {e}")
        
    finally:
        conn.close()
        print("\nПодключение к базе данных закрыто.")

if __name__ == "__main__":
    setup_database()