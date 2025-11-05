import sqlite3
from sqlite3 import Connection
from datetime import datetime


def get_connection(db_name: str = "coaching.db") -> Connection:
    """
    Создает соединение с базой данных SQLite. 
    Имя базы данных изменено с "library.db" на "coaching.db" для соответствия ERD.
    """
    # Включаем поддержку внешних ключей (Foreign Keys)
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


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
            Time_start TEXT, 
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

    # Вставка данных в Booking (для примера)
    cursor.execute("SELECT COUNT(*) FROM Booking")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        future = datetime(2025, 12, 10, 15, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
        
        bookings = [
            (1, 1, now, future, 1), 
            (2, 2, now, future, 2)  
        ]
        cursor.executemany("INSERT INTO Booking (Coach_ID, User_ID, Time_start, Time_end, Number_booking) VALUES (?, ?, ?, ?, ?)", bookings)
        print("Добавлены бронирования (Booking).")
        
    # Вставка данных в Booking_inventory (для примера)
    cursor.execute("SELECT COUNT(*) FROM Booking_inventory")
    if cursor.fetchone()[0] == 0:
        booking_inventories = [
            (1, 1, 2), 
            (3, 2, 1)  
        ]
        cursor.executemany("INSERT INTO Booking_inventory (Inventory_ID, Booking_ID, Status_ID) VALUES (?, ?, ?)", booking_inventories)
        print("Добавлены связи бронирования с инвентарем (Booking_inventory).")

    conn.commit()
    conn.close()

# --- ФУНКЦИИ УПРАВЛЕНИЯ ДАННЫМИ (Добавление) ---

def add_inventory_from_console(db_name: str = "coaching.db"):
    """Добавляет новый инвентарь в таблицу Inventory."""
    conn = get_connection(db_name)
    cursor = conn.cursor()
    print("\n--- Добавление нового Инвентаря ---")
    try:
        name = input("Введите название инвентаря: ")
        count = int(input("Введите количество: "))
        comment = input("Введите комментарий (можно оставить пустым): ")
        
        cursor.execute(
            "INSERT INTO Inventory (Name, Count, Comment) VALUES (?, ?, ?)",
            (name, count, comment)
        )
        conn.commit()
        print(f"✅ Инвентарь '{name}' успешно добавлен. ID: {cursor.lastrowid}")
    except ValueError:
        print("❌ Ошибка: Количество должно быть числом.")
    except Exception as e:
        print(f"❌ Произошла ошибка при добавлении инвентаря: {e}")
    finally:
        conn.close()

def add_coach_from_console(db_name: str = "coaching.db"):
    """Добавляет нового тренера в таблицу Coach."""
    conn = get_connection(db_name)
    cursor = conn.cursor()
    print("\n--- Добавление нового Тренера ---")
    try:
        surname = input("Введите фамилию тренера: ")
        name = input("Введите имя тренера: ")
        internal_number = int(input("Введите внутренний номер: "))
        experience = int(input("Введите стаж (лет): "))
        password = input("Введите пароль: ")
        
        cursor.execute(
            "INSERT INTO Coach (Internal_number, Surname, Name, Experience, Password) VALUES (?, ?, ?, ?, ?)",
            (internal_number, surname, name, experience, password)
        )
        conn.commit()
        print(f"✅ Тренер '{surname} {name}' успешно добавлен. ID: {cursor.lastrowid}")
    except ValueError:
        print("❌ Ошибка: Внутренний номер и стаж должны быть числами.")
    except Exception as e:
        print(f"❌ Произошла ошибка при добавлении тренера: {e}")
    finally:
        conn.close()

def add_user_from_console(db_name: str = "coaching.db"):
    """Добавляет нового пользователя в таблицу User."""
    conn = get_connection(db_name)
    cursor = conn.cursor()
    print("\n--- Добавление нового Пользователя ---")
    try:
        surname = input("Введите фамилию пользователя: ")
        name = input("Введите имя пользователя: ")
        password = input("Введите пароль: ")
        
        cursor.execute(
            "INSERT INTO User (Surname, Name, Password) VALUES (?, ?, ?)",
            (surname, name, password)
        )
        conn.commit()
        print(f"✅ Пользователь '{surname} {name}' успешно добавлен. ID: {cursor.lastrowid}")
    except Exception as e:
        print(f"❌ Произошла ошибка при добавлении пользователя: {e}")
    finally:
        conn.close()

def add_booking_from_console(db_name: str = "coaching.db"):
    conn = get_connection(db_name)
    cursor = conn.cursor()

    print("\n--- Добавление нового бронирования (Booking) ---")
    display_all_bookings_details(conn)
    
    print("\n**Справочные ID:**")
    cursor.execute("SELECT Coach_ID, Name, Surname FROM Coach")
    print("Тренеры:", [f"{r[0]} ({r[1]} {r[2]})" for r in cursor.fetchall()])

    cursor.execute("SELECT User_ID, Name, Surname FROM User")
    print("Пользователи:", [f"{r[0]} ({r[1]} {r[2]})" for r in cursor.fetchall()])

    cursor.execute("SELECT Inventory_ID, Name FROM Inventory")
    print("Инвентарь:", [f"{r[0]} ({r[1]})" for r in cursor.fetchall()])

    cursor.execute("SELECT Status_ID, Name FROM Status")
    print("Статусы:", [f"{r[0]} ({r[1]})" for r in cursor.fetchall()])

    try:
        coach_id = int(input("\nВведите ID Тренера (Coach_ID): "))
        user_id = int(input("Введите ID Пользователя (User_ID): "))
        time_start_str = input("Введите время начала (YYYY-MM-DD HH:MM:SS): ")
        time_end_str = input("Введите время окончания (YYYY-MM-DD HH:MM:SS): ")
        
        cursor.execute("SELECT IFNULL(MAX(Number_booking), 0) FROM Booking")
        next_booking_number = cursor.fetchone()[0] + 1
        
        cursor.execute(
            "INSERT INTO Booking (Coach_ID, User_ID, Time_start, Time_end, Number_booking) VALUES (?, ?, ?, ?, ?)",
            (coach_id, user_id, time_start_str, time_end_str, next_booking_number)
        )
        booking_id = cursor.lastrowid
        
        print(f"\nБронирование успешно добавлено. Booking_ID: {booking_id}")

        inventory_id = int(input("Введите ID Инвентаря (Inventory_ID) для бронирования: "))
        status_id = int(input("Введите ID Статуса (Status_ID) для этого инвентаря: "))

        cursor.execute(
            "INSERT INTO Booking_inventory (Inventory_ID, Booking_ID, Status_ID) VALUES (?, ?, ?)",
            (inventory_id, booking_id, status_id)
        )
        
        print(f"✅ Связь с инвентарем успешно добавлена. Booking_inventory_ID: {cursor.lastrowid}")
        
        conn.commit()

    except ValueError:
        print("❌ Ошибка: Введены некорректные данные. Убедитесь, что ID и время указаны правильно.")
    except sqlite3.IntegrityError:
        print("❌ Ошибка: Введен некорректный ID (тренер, пользователь, инвентарь или статус не найдены).")
    except Exception as e:
        print(f"❌ Произошла ошибка при добавлении в БД: {e}")
        
    conn.close()

# --- ФУНКЦИИ УПРАВЛЕНИЯ ДАННЫМИ (Изменение) ---

def modify_booking_from_console(db_name: str = "coaching.db"):
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    print("\n--- Изменение существующего бронирования (Booking) ---")
    
    if not display_all_bookings_details(conn):
        conn.close()
        return

    try:
        booking_id = int(input("\nВведите ID Бронирования (Booking_ID) для изменения: "))
        
        cursor.execute("SELECT * FROM Booking WHERE Booking_ID = ?", (booking_id,))
        booking_record = cursor.fetchone()
        
        if not booking_record:
            print(f"❌ Ошибка: Бронирование с ID {booking_id} не найдено.")
            conn.close()
            return
            
        print(f"\n--- Изменение записи Booking_ID: {booking_id} ---")

        print("Введите новое значение или оставьте поле пустым, чтобы не менять.")
        new_coach_id = input(f"Новый ID Тренера (текущий: {booking_record[1]}): ")
        new_user_id = input(f"Новый ID Пользователя (текущий: {booking_record[2]}): ")
        new_time_start = input(f"Новое время начала (текущее: {booking_record[3]}): ")
        new_time_end = input(f"Новое время окончания (текущее: {booking_record[4]}): ")

        update_fields = []
        params = []

        if new_coach_id:
            update_fields.append("Coach_ID = ?")
            params.append(int(new_coach_id))
        if new_user_id:
            update_fields.append("User_ID = ?")
            params.append(int(new_user_id))
        if new_time_start:
            update_fields.append("Time_start = ?")
            params.append(new_time_start)
        if new_time_end:
            update_fields.append("Time_end = ?")
            params.append(new_time_end)

        if update_fields:
            sql_update_booking = "UPDATE Booking SET " + ", ".join(update_fields) + " WHERE Booking_ID = ?"
            params.append(booking_id)
            cursor.execute(sql_update_booking, tuple(params))
            print("✅ Запись Booking обновлена.")
        else:
            print("Запись Booking не изменена.")
            
        cursor.execute("SELECT Inventory_ID, Status_ID FROM Booking_inventory WHERE Booking_ID = ?", (booking_id,))
        inventory_record = cursor.fetchone()
        
        if inventory_record:
            old_inventory_id = inventory_record[0]
            old_status_id = inventory_record[1]
            
            print(f"\n--- Изменение связанного инвентаря (Booking_inventory) ---")
            
            new_inventory_id = input(f"Новый ID Инвентаря (текущий: {old_inventory_id}): ")
            new_status_id = input(f"Новый ID Статуса (текущий: {old_status_id}): ")
            
            update_fields_inv = []
            params_inv = []
            
            if new_inventory_id:
                update_fields_inv.append("Inventory_ID = ?")
                params_inv.append(int(new_inventory_id))
            if new_status_id:
                update_fields_inv.append("Status_ID = ?")
                params_inv.append(int(new_status_id))
                
            if update_fields_inv:
                sql_update_inventory = "UPDATE Booking_inventory SET " + ", ".join(update_fields_inv) + " WHERE Booking_ID = ?"
                params_inv.append(booking_id)
                cursor.execute(sql_update_inventory, tuple(params_inv))
                print("✅ Запись Booking_inventory обновлена.")
            else:
                print("Запись Booking_inventory не изменена.")
        else:
            print("Связанный инвентарь для этого бронирования не найден.")
            
        conn.commit()
        print("\n✅ Изменения успешно сохранены.")

    except ValueError:
        print("❌ Ошибка: Введены некорректные данные. ID и другие числовые поля должны быть числами.")
    except sqlite3.IntegrityError:
        print("❌ Ошибка: Нарушение внешнего ключа. Убедитесь, что введенные ID (тренера/пользователя/инвентаря/статуса) существуют.")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        
    conn.close()

def modify_user_from_console(db_name: str = "coaching.db"):
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    print("\n--- Изменение данных Пользователя (User) ---")
    
    if not display_all_users_details(conn):
        conn.close()
        return

    try:
        user_id = int(input("\nВведите ID Пользователя (User_ID) для изменения: "))
        
        cursor.execute("SELECT User_ID, Surname, Name, Password FROM User WHERE User_ID = ?", (user_id,))
        user_record = cursor.fetchone()
        
        if not user_record:
            print(f"❌ Ошибка: Пользователь с ID {user_id} не найден.")
            conn.close()
            return
            
        old_surname, old_name, old_password = user_record[1], user_record[2], user_record[3]
            
        print(f"\n--- Изменение записи Пользователя ID: {user_id} (Текущее имя: {old_name} {old_surname}) ---")

        print("Введите новое значение или оставьте поле пустым, чтобы не менять.")
        new_surname = input(f"Новая Фамилия (текущая: {old_surname}): ")
        new_name = input(f"Новое Имя (текущее: {old_name}): ")
        new_password = input(f"Новый Пароль (текущий: ****): ") 

        update_fields = []
        params = []

        if new_surname:
            update_fields.append("Surname = ?")
            params.append(new_surname)
        if new_name:
            update_fields.append("Name = ?")
            params.append(new_name)
        if new_password:
            update_fields.append("Password = ?")
            params.append(new_password)

        if update_fields:
            sql_update_user = "UPDATE User SET " + ", ".join(update_fields) + " WHERE User_ID = ?"
            params.append(user_id)
            cursor.execute(sql_update_user, tuple(params))
            conn.commit()
            print("✅ Запись Пользователя успешно обновлена.")
        else:
            print("Запись Пользователя не изменена.")
            
    except ValueError:
        print("❌ Ошибка: Введены некорректные данные. ID должно быть числом.")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        
    conn.close()

def modify_inventory_from_console(db_name: str = "coaching.db"):
    """
    Позволяет выбрать элемент инвентаря по ID и изменить его название, количество или комментарий.
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    print("\n--- Изменение данных Инвентаря (Inventory) ---")
    
    if not display_all_inventory_details(conn):
        conn.close()
        return

    try:
        inventory_id = int(input("\nВведите ID Инвентаря (Inventory_ID) для изменения: "))
        
        # Проверяем существование записи Inventory
        cursor.execute("SELECT Inventory_ID, Name, Count, Comment FROM Inventory WHERE Inventory_ID = ?", (inventory_id,))
        inventory_record = cursor.fetchone()
        
        if not inventory_record:
            print(f"❌ Ошибка: Инвентарь с ID {inventory_id} не найден.")
            conn.close()
            return
            
        old_name, old_count, old_comment = inventory_record[1], inventory_record[2], inventory_record[3]
            
        print(f"\n--- Изменение записи Инвентаря ID: {inventory_id} (Текущее название: {old_name}, Количество: {old_count}) ---")

        print("Введите новое значение или оставьте поле пустым, чтобы не менять.")
        new_name = input(f"Новое Название (текущее: {old_name}): ")
        new_count_str = input(f"Новое Количество (текущее: {old_count}): ")
        new_comment = input(f"Новый Комментарий (текущий: {old_comment if old_comment else 'пусто'}): ")

        update_fields = []
        params = []

        if new_name:
            update_fields.append("Name = ?")
            params.append(new_name)
        
        if new_count_str:
            new_count = int(new_count_str) # Преобразуем в число, здесь может быть ValueError
            update_fields.append("Count = ?")
            params.append(new_count)
            
        # SQLite позволяет вставлять NULL, если в таблице нет NOT NULL
        if new_comment:
            update_fields.append("Comment = ?")
            params.append(new_comment)
        # Если пользователь хочет очистить комментарий
        elif new_comment == '':
            update_fields.append("Comment = NULL")
            
        if update_fields:
            sql_update_inventory = "UPDATE Inventory SET " + ", ".join(update_fields) + " WHERE Inventory_ID = ?"
            params.append(inventory_id)
            cursor.execute(sql_update_inventory, tuple(params))
            conn.commit()
            print("✅ Запись Инвентаря успешно обновлена.")
        else:
            print("Запись Инвентаря не изменена.")
            
    except ValueError:
        print("❌ Ошибка: Введены некорректные данные. ID и Количество должны быть числами.")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        
    conn.close()

# --- ФУНКЦИИ ПРОСМОТРА (Utility) ---

def display_all_bookings_details(conn: Connection) -> bool:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            T3.Booking_ID, 
            T3.Time_start, 
            T3.Time_end,
            T1.Name || ' ' || T1.Surname AS User, 
            T2.Name || ' ' || T2.Surname AS Coach, 
            T4.Name AS Inventory_Name, 
            T5.Name AS Status_Name
        FROM User T1 
        JOIN Booking T3 ON T1.User_ID = T3.User_ID 
        JOIN Coach T2 ON T2.Coach_ID = T3.Coach_ID 
        JOIN Booking_inventory T6 ON T3.Booking_ID = T6.Booking_ID 
        JOIN Inventory T4 ON T4.Inventory_ID = T6.Inventory_ID 
        JOIN Status T5 ON T5.Status_ID = T6.Status_ID
        ORDER BY T3.Booking_ID
    """)
    bookings = cursor.fetchall()

    if not bookings:
        print("ℹ️ В базе данных нет существующих бронирований для просмотра/изменения.")
        return False
        
    print("\n--- Детали Бронирований ---")
    print("=========================================================================================")
    print("| Booking_ID | Start Time          | End Time            | User        | Coach       | Inventory | Status    |")
    print("=========================================================================================")
    for row in bookings:
        print(f"| {row[0]:<10} | {row[1]:<19} | {row[2]:<19} | {row[3]:<11} | {row[4]:<11} | {row[5]:<9} | {row[6]:<9} |")
    print("=========================================================================================")
    return True

def display_all_users_details(conn: Connection) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT User_ID, Surname, Name, Password FROM User ORDER BY User_ID")
    users = cursor.fetchall()
    
    if not users:
        print("ℹ️ В базе данных нет существующих пользователей.")
        return False

    print("\n--- Доступные Пользователи ---")
    print("==============================================")
    print("| User_ID | Фамилия   | Имя       | Пароль   |")
    print("==============================================")
    for row in users:
        password_masked = '*' * len(row[3]) 
        print(f"| {row[0]:<7} | {row[1]:<9} | {row[2]:<9} | {password_masked:<8} |")
    print("==============================================")
    return True

def display_all_inventory_details(conn: Connection) -> bool:
    """Отображает весь существующий инвентарь."""
    cursor = conn.cursor()
    cursor.execute("SELECT Inventory_ID, Name, Count, Comment FROM Inventory ORDER BY Inventory_ID")
    inventory = cursor.fetchall()
    
    if not inventory:
        print("ℹ️ В базе данных нет существующего инвентаря.")
        return False

    print("\n--- Доступный Инвентарь ---")
    print("=================================================================")
    print("| Inventory_ID | Название            | Кол-во | Комментарий       |")
    print("=================================================================")
    for row in inventory:
        comment_display = row[3] if row[3] else '---'
        print(f"| {row[0]:<12} | {row[1]:<19} | {row[2]:<6} | {comment_display:<15} |")
    print("=================================================================")
    return True

from typing import Dict, Tuple, Callable, List

# --- КАРТА ДЕЙСТВИЙ И ПОЛИТИКА РОЛЕЙ ---

# Определяем все возможные действия и функции, которые они вызывают.
ACTION_MAP: Dict[str, Tuple[str, Callable]] = {
    # (Описание в меню, Функция для вызова)
    "ADD_COACH": ("Добавить нового Тренера", add_coach_from_console),
    "ADD_USER": ("Добавить нового Пользователя", add_user_from_console),
    "MODIFY_USER": ("Изменить данные Пользователя", modify_user_from_console),
    "ADD_INVENTORY": ("Добавить Инвентарь", add_inventory_from_console),
    "MODIFY_INVENTORY": ("Изменить данные Инвентаря", modify_inventory_from_console),
    "ADD_BOOKING": ("Добавить новое Бронирование", add_booking_from_console),
    "MODIFY_BOOKING": ("Изменить существующее Бронирование", modify_booking_from_console),
}

# Определяем, какие КЛЮЧИ действий доступны для каждой роли
ROLE_POLICY: Dict[str, List[str]] = {
    "Администратор": [
        "ADD_COACH", "ADD_USER", "MODIFY_USER", 
        "ADD_INVENTORY", "MODIFY_INVENTORY", 
        "ADD_BOOKING", "MODIFY_BOOKING"
    ],
    "Тренер": [
        "ADD_BOOKING", "MODIFY_BOOKING"
    ],
    "Пользователь": [
        "ADD_BOOKING",
    ]
}

# --- ФУНКЦИИ УПРАВЛЕНИЯ БД (СУЩЕСТВУЮЩИЕ) ---

def get_connection(db_name: str = "coaching.db") -> Connection:
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# --- ФУНКЦИЯ АУТЕНТИФИКАЦИИ (Новая) ---

def authenticate_user(db_name: str, username: str, password: str) -> str | None:
    """
    Проверяет логин и пароль в таблицах Coach и User и возвращает роль.
    
    Логика:
    1. Ищем в таблице Coach по Internal_number (username)
    2. Если не найдено, ищем в таблице User по User_ID (username).
    3. Специальный логин "admin" ведет к проверке Coach с Internal_number 999.
    
    Возвращает: 'Администратор', 'Тренер', 'Пользователь' или None.
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()
    role = None
    
    try:
        # 1. Попытка аутентификации как Администратор (специальный логин 'admin')
        if username.lower() == 'admin':
            cursor.execute("SELECT Coach_ID FROM Coach WHERE Internal_number = 999 AND Password = ?", (password,))
            if cursor.fetchone():
                role = "Администратор"
                
        # 2. Попытка аутентификации как Тренер (логин: Internal_number)
        elif not role:
            # Преобразование логина в число для Internal_number
            try:
                internal_number = int(username)
                cursor.execute("SELECT Coach_ID FROM Coach WHERE Internal_number = ? AND Password = ?", (internal_number, password))
                if cursor.fetchone():
                    role = "Тренер"
            except ValueError:
                pass # Пропускаем, если логин не числовой

        # 3. Попытка аутентификации как Пользователь (логин: User_ID)
        if not role:
            # Преобразование логина в число для User_ID
            try:
                user_id = int(username)
                cursor.execute("SELECT User_ID FROM User WHERE User_ID = ? AND Password = ?", (user_id, password))
                if cursor.fetchone():
                    role = "Пользователь"
            except ValueError:
                pass # Пропускаем, если логин не числовой
                
    except Exception as e:
        print(f"Ошибка БД при аутентификации: {e}")
        
    finally:
        conn.close()
        
    return role

# --- ГЛАВНОЕ МЕНЮ (Из вашего запроса) ---

def main_menu(db_name: str, current_user_role: str):
    """
    Динамически строит и обрабатывает меню на основе роли пользователя
    и централизованных политик.
    """
    # 1. Получаем ключи доступных действий для текущей роли
    if current_user_role not in ROLE_POLICY:
        print("Ошибка: Неизвестная роль.")
        return

    allowed_action_keys = ROLE_POLICY[current_user_role]
    
    # 2. Создаем финальный словарь (ключ_выбора: (описание, функция))
    current_menu_actions = {}
    i = 1
    
    for action_key in allowed_action_keys:
        if action_key in ACTION_MAP:
            # Используем строковое представление i как ключ выбора
            current_menu_actions[str(i)] = ACTION_MAP[action_key]
            i += 1
    
    # === 3. Отображение и обработка (логика, которая всегда одинакова) ===
    while True:
        print("\n" + "="*40)
        print(f"       МЕНЮ: {current_user_role.upper()}")
        print("="*40)
        
        # Печатаем пункты меню из динамически созданного словаря
        for key, (description, _) in current_menu_actions.items():
            print(f"{key}. {description}")
            
        print("0. Выход/Смена пользователя")
        print("="*40)
        
        choice = input("Выберите действие: ")
        
        if choice == '0':
            print(f"\nВыход из системы. До свидания!")
            break
        elif choice in current_menu_actions:
            # Вызов функции: current_menu_actions[choice] возвращает кортеж (описание, функция)
            function_to_call = current_menu_actions[choice][1]
            function_to_call(db_name) # Предполагаем, что все функции принимают db_name
        else:
            print("Некорректный ввод. Пожалуйста, выберите номер из списка.")

# --- ОСНОВНАЯ ТОЧКА ВХОДА (start_program) ---

def start_program(db_name: str = "coaching.db"):
    """
    Основная точка входа с циклом аутентификации.
    """
    while True:
        print("\n" + "="*40)
        print("       СИСТЕМА УПРАВЛЕНИЯ КОУЧИНГОМ")
        print("="*40)
        print("Подсказки для входа:")
        print(" - Админ: Логин=admin, Пароль=admin_pass")
        print(" - Тренер (Петр Иванов): Логин=101, Пароль=pass101")
        print(" - Пользователь (Алексей Климов): Логин=1, Пароль=userpass1")
        
        username = input("Введите Логин (Internal_number/User_ID/admin): ")
        password = input("Введите Пароль: ")
        
        current_user_role = authenticate_user(db_name, username, password)
        
        if current_user_role:
            print(f"✅ Добро пожаловать, {username}! Ваша роль: **{current_user_role}**.")
            # Передаем управление в главное меню
            main_menu(db_name, current_user_role)
            # После выхода из main_menu (по выбору '0') цикл продолжается 
            # и снова предложит аутентификацию.
        else:
            print("❌ Ошибка аутентификации. Неверный логин или пароль.")
        
        continue_choice = input("Хотите попробовать войти снова? (д/н): ").lower()
        if continue_choice != 'д':
            break

# --- ПРИМЕР ЗАПУСКА ---

if __name__ == '__main__':
    # ... (Остальные функции: create_tables, insert_sample_data, add_*, modify_*, display_* # должны быть здесь для полноценного запуска)
    
    # Для целей демонстрации, добавим заглушки функций, если они были опущены:
    def create_tables(db_name: str = "coaching.db"): print("Создание таблиц...")
    def insert_sample_data(db_name: str = "coaching.db"): print("Вставка тестовых данных...")
    def add_coach_from_console(db_name: str = "coaching.db"): print("Добавление тренера...")
    def add_user_from_console(db_name: str = "coaching.db"): print("Добавление пользователя...")
    def modify_user_from_console(db_name: str = "coaching.db"): print("Изменение пользователя...")
    def add_inventory_from_console(db_name: str = "coaching.db"): print("Добавление инвентаря...")
    def modify_inventory_from_console(db_name: str = "coaching.db"): print("Изменение инвентаря...")
    def add_booking_from_console(db_name: str = "coaching.db"): print("Добавление бронирования...")
    def modify_booking_from_console(db_name: str = "coaching.db"): print("Изменение бронирования...")
    def display_all_inventory_details(conn): print("Просмотр инвентаря...")
    def display_all_bookings_details(conn): print("Просмотр бронирований...")
    
    # Запуск
    DB_NAME = "coaching.db"
    
    # Предполагается, что эти функции уже создают БД и наполняют ее данными
    create_tables(DB_NAME)
    insert_sample_data(DB_NAME) 
    
    # Начинаем программу с аутентификации
    start_program(DB_NAME)

    # Финальная проверка после выхода
    try:
        conn = get_connection(DB_NAME)
        print("\n--- Финальная проверка ---")
        display_all_bookings_details(conn)
        conn.close()
    except Exception:
        pass
