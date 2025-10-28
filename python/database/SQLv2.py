import sqlite3
from sqlite3 import Connection
from datetime import datetime

# Вспомогательная функция, остается неизменной
def get_connection(db_name: str = "coaching.db") -> Connection:
    """
    Создает соединение с базой данных SQLite. 
    Имя базы данных изменено с "library.db" на "coaching.db" для соответствия ERD.
    """
    return sqlite3.connect(db_name)

# Функция для создания таблиц, переработанная под ERD
def create_tables(db_name: str = "coaching.db"):
    """
    Создает таблицы, соответствующие предоставленной ERD:
    Coach, User, Inventory, Status, Booking, Booking_inventory.
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()

    # 1. Таблица Coach
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Coach (
            Coach_ID INTEGER PRIMARY KEY,
            Internal_number INTEGER,
            Surname TEXT NOT NULL,
            Name TEXT NOT NULL,
            Experience INTEGER,
            Password TEXT NOT NULL
        )
    ''')

    # 2. Таблица User
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            User_ID INTEGER PRIMARY KEY,
            Surname TEXT NOT NULL,
            Name TEXT NOT NULL,
            Password TEXT NOT NULL
        )
    ''')

    # 3. Таблица Inventory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Inventory (
            Inventory_ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Count INTEGER,
            Comment TEXT
        )
    ''')

    # 4. Таблица Status
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Status (
            Status_ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL UNIQUE,
            Comment TEXT
        )
    ''')

    # 5. Таблица Booking (со связями Coach и User)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Booking (
            Booking_ID INTEGER PRIMARY KEY,
            Coach_ID INTEGER,
            User_ID INTEGER,
            Time_start TEXT, -- Использован TEXT для совместимости с SQLite date/time
            Time_end TEXT, 
            Number_booking INTEGER,
            FOREIGN KEY (Coach_ID) REFERENCES Coach(Coach_ID),
            FOREIGN KEY (User_ID) REFERENCES User(User_ID)
        )
    ''')
    
    # 6. Таблица Booking_inventory (связующая таблица с Inventory и Status)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Booking_inventory (
            Booking_inventory_ID INTEGER PRIMARY KEY,
            Inventory_ID INTEGER,
            Booking_ID INTEGER,
            Status_ID INTEGER,
            FOREIGN KEY (Inventory_ID) REFERENCES Inventory(Inventory_ID),
            FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID),
            FOREIGN KEY (Status_ID) REFERENCES Status(Status_ID)
        )
    ''')

    conn.commit()
    conn.close()


# Функция для вставки тестовых данных, переработанная под ERD
def insert_sample_data(db_name: str = "coaching.db"):
    """
    Вставляет тестовые записи во все таблицы ERD, если они еще не добавлены.
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    # Вставка данных в Status
    cursor.execute("SELECT COUNT(*) FROM Status")
    if cursor.fetchone()[0] == 0:
        statuses = [
            ("Забронировано", "Ожидает подтверждения"),
            ("Подтверждено", "Бронирование активно"),
            ("Отменено", "Бронирование отменено пользователем"),
            ("Завершено", "Услуга оказана")
        ]
        cursor.executemany("INSERT INTO Status (Name, Comment) VALUES (?, ?)", statuses)
        print("Добавлены статусы.")

    # Вставка данных в Coach
    cursor.execute("SELECT COUNT(*) FROM Coach")
    if cursor.fetchone()[0] == 0:
        coaches = [
            (101, "Иванов", "Петр", 5, "pass101"),
            (102, "Сидорова", "Мария", 8, "pass102")
        ]
        cursor.executemany("INSERT INTO Coach (Internal_number, Surname, Name, Experience, Password) VALUES (?, ?, ?, ?, ?)", coaches)
        print("Добавлены тренеры (Coach).")

    # Вставка данных в User
    cursor.execute("SELECT COUNT(*) FROM User")
    if cursor.fetchone()[0] == 0:
        users = [
            ("Климов", "Алексей", "userpass1"),
            ("Орлова", "Елена", "userpass2")
        ]
        cursor.executemany("INSERT INTO User (Surname, Name, Password) VALUES (?, ?, ?)", users)
        print("Добавлены пользователи (User).")
        
    # Вставка данных в Inventory
    cursor.execute("SELECT COUNT(*) FROM Inventory")
    if cursor.fetchone()[0] == 0:
        inventory_items = [
            ("Мяч для фитнеса", 5, "Стандартный диаметр"),
            ("Коврик для йоги", 10, "С противоскользящим покрытием"),
            ("Гантели 5кг", 2, "Пара")
        ]
        cursor.executemany("INSERT INTO Inventory (Name, Count, Comment) VALUES (?, ?, ?)", inventory_items)
        print("Добавлено оборудование (Inventory).")

    # Вставка данных в Booking
    cursor.execute("SELECT COUNT(*) FROM Booking")
    if cursor.fetchone()[0] == 0:
        # Получаем текущие дату/время для примеров
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        future = datetime(2025, 12, 10, 15, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
        
        bookings = [
            (1, 1, now, future, 1), # Тренер 1, Пользователь 1, Бронирование #1
            (2, 2, now, future, 2)  # Тренер 2, Пользователь 2, Бронирование #2
        ]
        # Обратите внимание: Coach_ID и User_ID соответствуют PK из таблиц Coach и User (т.е. 1 и 2)
        cursor.executemany("INSERT INTO Booking (Coach_ID, User_ID, Time_start, Time_end, Number_booking) VALUES (?, ?, ?, ?, ?)", bookings)
        print("Добавлены бронирования (Booking).")
        
    # Вставка данных в Booking_inventory (связывает бронирование с инвентарем и статусом)
    cursor.execute("SELECT COUNT(*) FROM Booking_inventory")
    if cursor.fetchone()[0] == 0:
        # Inventory_ID=1 (Мяч), Booking_ID=1, Status_ID=2 (Подтверждено)
        # Inventory_ID=3 (Гантели), Booking_ID=2, Status_ID=1 (Забронировано)
        booking_inventories = [
            (1, 1, 2), 
            (3, 2, 1)  
        ]
        cursor.executemany("INSERT INTO Booking_inventory (Inventory_ID, Booking_ID, Status_ID) VALUES (?, ?, ?)", booking_inventories)
        print("Добавлены связи бронирования с инвентарем (Booking_inventory).")

    conn.commit()
    conn.close()

# Пример запуска (для проверки):
if __name__ == '__main__':
    DB_NAME = "coaching.db"
    
    # Создаем таблицы
    create_tables(DB_NAME)
    print(f"\nТаблицы созданы в '{DB_NAME}'.")
    
    # Вставляем данные
    insert_sample_data(DB_NAME)
    
    # Проверяем, что данные были добавлены (опционально)
    conn = get_connection(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT T1.Name AS User_Name, T2.Name AS Coach_Name, T3.Time_start, T4.Name AS Inventory_Name, T5.Name AS Status_Name FROM User T1 JOIN Booking T3 ON T1.User_ID = T3.User_ID JOIN Coach T2 ON T2.Coach_ID = T3.Coach_ID JOIN Booking_inventory T6 ON T3.Booking_ID = T6.Booking_ID JOIN Inventory T4 ON T4.Inventory_ID = T6.Inventory_ID JOIN Status T5 ON T5.Status_ID = T6.Status_ID")
    print("\nПример данных (User, Coach, Start Time, Inventory, Status):")
    for row in cursor.fetchall():
        print(row)
    conn.close()