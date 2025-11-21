import sqlite3
from sqlite3 import Connection
from datetime import datetime

DB_NAME = "coaching.db"

# 1. УПРАВЛЕНИЕ БД: СОЕДИНЕНИЕ И СТРУКТУРА

def get_connection(db_name: str = "coaching.db") -> Connection:
    """Создает соединение с базой данных SQLite с поддержкой внешних ключей."""
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(db_name: str = "coaching.db"):
    """Создает все необходимые таблицы в БД."""
    conn = get_connection(db_name)
    cursor = conn.cursor()

    # 1. Coach (Тренер)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Coach (
            Coach_ID INTEGER PRIMARY KEY,
            Internal_number INTEGER UNIQUE NOT NULL,
            Surname TEXT NOT NULL,
            Name TEXT NOT NULL,
            Experience INTEGER DEFAULT 0,
            Password TEXT NOT NULL -- В реальном приложении это должен быть ХЭШ!
        )
    ''')

    # 2. User (Пользователь)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            User_ID INTEGER PRIMARY KEY,
            Surname TEXT NOT NULL,
            Name TEXT NOT NULL,
            Password TEXT NOT NULL -- В реальном приложении это должен быть ХЭШ!
        )
    ''')
    
    # 3. Inventory (Инвентарь)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Inventory (
            Inventory_ID INTEGER PRIMARY KEY,
            Name TEXT UNIQUE NOT NULL,
            Count INTEGER NOT NULL
        )
    ''')

    # 4. Status (Статус инвентаря)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Status (
            Status_ID INTEGER PRIMARY KEY,
            Name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # 5. Booking (Бронирование)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Booking (
            Booking_ID INTEGER PRIMARY KEY,
            Coach_ID INTEGER NOT NULL,
            User_ID INTEGER NOT NULL,
            Time_start TEXT NOT NULL,
            Time_end TEXT NOT NULL,
            Number_booking INTEGER NOT NULL,
            FOREIGN KEY (Coach_ID) REFERENCES Coach(Coach_ID),
            FOREIGN KEY (User_ID) REFERENCES User(User_ID)
        )
    ''')

    # 6. Booking_inventory (Связка бронирования и инвентаря)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Booking_inventory (
            Booking_ID INTEGER NOT NULL,
            Inventory_ID INTEGER NOT NULL,
            Status_ID INTEGER NOT NULL,
            PRIMARY KEY (Booking_ID, Inventory_ID),
            FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID) ON DELETE CASCADE,
            FOREIGN KEY (Inventory_ID) REFERENCES Inventory(Inventory_ID),
            FOREIGN KEY (Status_ID) REFERENCES Status(Status_ID)
        )
    ''')

    conn.commit()
    conn.close()

# 2. ТЕСТОВЫЕ ДАННЫЕ

def insert_sample_data(db_name: str = "coaching.db"):
    """Вставляет тестовые данные для проверки работы системы."""
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже данные
    if cursor.execute("SELECT COUNT(*) FROM Coach").fetchone()[0] > 0:
        conn.close()
        return 

    # 1. Coach (Тренер)
    coaches_data = [
        # Администратор системы, который числится как Coach
        (1, 'Adminov', 'Admin', 5, 'admin_pass'), 
        (101, 'Sidorova', 'Elena', 5, 'pass101'),
        (102, 'Ivanov', 'Petr', 3, 'pass102')
    ]
    cursor.executemany("INSERT INTO Coach (Internal_number, Surname, Name, Experience, Password) VALUES (?, ?, ?, ?, ?)", coaches_data)
    
    # 2. User (Пользователь)
    users_data = [
        ('Klimov', 'Alexey', 'userpass1'),
        ('Smirnova', 'Maria', 'userpass2'),
        ('Vorobyov', 'Ilya', 'userpass3')
    ]
    cursor.executemany("INSERT INTO User (Surname, Name, Password) VALUES (?, ?, ?)", users_data)
    
    # 3. Inventory (Инвентарь)
    inventory_data = [
        ('Штанга 20кг', 5, "Смотри чтоб не придавило"),
        ('Гантели 5кг', 10, "Кто их приклеил?"),
        ('Коврик для йоги', 20, "Для любимых поз")
    ]
    cursor.executemany("INSERT INTO Inventory (Name, Count, Comment) VALUES (?, ?, ?)", inventory_data)

    # 4. Status (Статус)
    status_data = [
        ('Забронировано',),
        ('В использовании',),
        ('Доступно',),
        ('Возвращено',)
    ]
    cursor.executemany("INSERT INTO Status (Name) VALUES (?)", status_data)

    # 5. Booking (Бронирование)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    future = datetime(2025, 12, 31, 15, 0).strftime("%Y-%m-%d %H:%M:%S")
    
    # Coach_ID 2 (Sidorova), User_ID 1 (Klimov)
    bookings_data = [
        (2, 1, now, future, 1001), 
        (3, 2, now, future, 1002) # Coach_ID 3 (Ivanov), User_ID 2 (Smirnova)
    ]
    cursor.executemany("INSERT INTO Booking (Coach_ID, User_ID, Time_start, Time_end, Number_booking) VALUES (?, ?, ?, ?, ?)", bookings_data)

    # 6. Booking_inventory (Инвентарь для бронирования)
    # Booking 1001 (ID=1): Штанга 20кг (ID=1), Статус "В использовании" (ID=2)
    # Booking 1002 (ID=2): Коврик для йоги (ID=3), Статус "Забронировано" (ID=1)
    booking_inventory_data = [
        (1, 1, 2),
        (2, 3, 1)
    ]
    cursor.executemany("INSERT INTO Booking_inventory (Booking_ID, Inventory_ID, Status_ID) VALUES (?, ?, ?)", booking_inventory_data)

    conn.commit()
    conn.close()