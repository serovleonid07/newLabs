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

# НОВАЯ ФУНКЦИЯ: Добавление бронирования из консоли
def add_booking_from_console(db_name: str = "coaching.db"):
    """
    Позволяет пользователю добавить новое бронирование и связать его с инвентарем и статусом 
    через ввод данных в консоли.
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()

    print("\n--- Добавление нового бронирования ---")

    # 1. Показать доступные ID для выбора
    print("\n**Доступные Тренеры:**")
    cursor.execute("SELECT Coach_ID, Name, Surname FROM Coach")
    coaches = cursor.fetchall()
    for row in coaches:
        print(f"ID: {row[0]}, Имя: {row[1]} {row[2]}")

    print("\n**Доступные Пользователи:**")
    cursor.execute("SELECT User_ID, Name, Surname FROM User")
    users = cursor.fetchall()
    for row in users:
        print(f"ID: {row[0]}, Имя: {row[1]} {row[2]}")

    print("\n**Доступный Инвентарь:**")
    cursor.execute("SELECT Inventory_ID, Name FROM Inventory")
    inventory_items = cursor.fetchall()
    for row in inventory_items:
        print(f"ID: {row[0]}, Название: {row[1]}")

    print("\n**Доступные Статусы:**")
    cursor.execute("SELECT Status_ID, Name FROM Status")
    statuses = cursor.fetchall()
    for row in statuses:
        print(f"ID: {row[0]}, Статус: {row[1]}")

    # 2. Получить данные бронирования
    try:
        coach_id = int(input("\nВведите ID Тренера (Coach_ID): "))
        user_id = int(input("Введите ID Пользователя (User_ID): "))
        # Ввод даты и времени
        time_start_str = input("Введите время начала (YYYY-MM-DD HH:MM:SS, например, 2025-12-15 10:00:00): ")
        time_end_str = input("Введите время окончания (YYYY-MM-DD HH:MM:SS, например, 2025-12-15 11:00:00): ")
        
        # Автоматический расчет Number_booking
        cursor.execute("SELECT IFNULL(MAX(Number_booking), 0) FROM Booking")
        next_booking_number = cursor.fetchone()[0] + 1
        
        # 3. Вставить запись в Booking
        cursor.execute(
            "INSERT INTO Booking (Coach_ID, User_ID, Time_start, Time_end, Number_booking) VALUES (?, ?, ?, ?, ?)",
            (coach_id, user_id, time_start_str, time_end_str, next_booking_number)
        )
        booking_id = cursor.lastrowid
        
        print(f"\nБронирование успешно добавлено. Booking_ID: {booking_id}")

        # 4. Получить данные Booking_inventory
        inventory_id = int(input("Введите ID Инвентаря (Inventory_ID) для бронирования: "))
        status_id = int(input("Введите ID Статуса (Status_ID) для этого инвентаря: "))

        # 5. Вставить запись в Booking_inventory
        cursor.execute(
            "INSERT INTO Booking_inventory (Inventory_ID, Booking_ID, Status_ID) VALUES (?, ?, ?)",
            (inventory_id, booking_id, status_id)
        )
        
        print(f"Связь с инвентарем успешно добавлена. Booking_inventory_ID: {cursor.lastrowid}")
        
        conn.commit()

    except ValueError:
        print("\nОшибка: Введены некорректные данные. Убедитесь, что ID являются числами.")
    except Exception as e:
        print(f"\nПроизошла ошибка при добавлении в БД: {e}")
        
    conn.close()

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

# --- ФУНКЦИЯ ИЗМЕНЕНИЯ ПРОШЛЫХ ЗАПИСЕЙ (Modification) ---

def modify_booking_from_console(db_name: str = "coaching.db"):
    """
    Позволяет выбрать существующее бронирование по ID и изменить его данные.
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    print("\n--- Изменение существующего бронирования (Booking) ---")
    
    if not display_all_bookings_details(conn):
        conn.close()
        return

    try:
        booking_id = int(input("\nВведите ID Бронирования (Booking_ID) для изменения: "))
        
        # Проверяем существование записи Booking
        cursor.execute("SELECT * FROM Booking WHERE Booking_ID = ?", (booking_id,))
        booking_record = cursor.fetchone()
        
        if not booking_record:
            print(f"❌ Ошибка: Бронирование с ID {booking_id} не найдено.")
            conn.close()
            return
            
        print(f"\n--- Изменение записи Booking_ID: {booking_id} ---")

        # Изменение Booking
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
            
        # --- Изменение Booking_inventory ---
        
        # Находим связанный инвентарь
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

def display_all_users_details(conn: Connection) -> bool:
    """Отображает всех существующих пользователей."""
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
        # Скрываем пароль звездочками для безопасности
        password_masked = '*' * len(row[3]) 
        print(f"| {row[0]:<7} | {row[1]:<9} | {row[2]:<9} | {password_masked:<8} |")
    print("==============================================")
    return True

def modify_user_from_console(db_name: str = "coaching.db"):
    """
    Позволяет выбрать существующего пользователя по ID и изменить его данные.
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    print("\n--- Изменение данных Пользователя (User) ---")
    
    # Показываем список пользователей для выбора
    if not display_all_users_details(conn):
        conn.close()
        return

    try:
        user_id = int(input("\nВведите ID Пользователя (User_ID) для изменения: "))
        
        # Проверяем существование записи User
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
        new_password = input(f"Новый Пароль (текущий: ****): ") # Не показываем текущий пароль

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

# --- ФУНКЦИЯ ПРОСМОТРА (Utility) ---

def display_all_bookings_details(conn: Connection) -> bool:
    """Отображает все существующие бронирования с деталями."""
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
        
    print("\n=========================================================================================")
    print("| Booking_ID | Start Time          | End Time            | User        | Coach       | Inventory | Status    |")
    print("=========================================================================================")
    for row in bookings:
        print(f"| {row[0]:<10} | {row[1]:<19} | {row[2]:<19} | {row[3]:<11} | {row[4]:<11} | {row[5]:<9} | {row[6]:<9} |")
    print("=========================================================================================")
    return True

# --- ГЛАВНОЕ МЕНЮ ---

def main_menu(db_name: str = "coaching.db"):
    """
    Показывает меню выбора действий: добавление различных сущностей, изменение или выход.
    """
    while True:
        print("\n" + "="*40)
        print("           МЕНЮ УПРАВЛЕНИЯ ДАННЫМИ")
        print("="*40)
        print("1. Добавить нового Тренера (Coach)")
        print("2. Добавить нового Пользователя (User)")
        print("3. Добавить Инвентарь (Inventory)")
        print("4. Добавить новое Бронирование (Booking)")
        print("---")
        print("5. Изменить существующее Бронирование (Booking)")
        print("6. Изменить данные Пользователя (User) <--- НОВИНКА")
        print("0. Завершить работу и проверить данные")
        print("="*40)

        choice = input("Выберите действие (0-6): ")

        if choice == '1':
            add_coach_from_console(db_name)
        elif choice == '2':
            add_user_from_console(db_name)
        elif choice == '3':
            add_inventory_from_console(db_name)
        elif choice == '4':
            add_booking_from_console(db_name)
        elif choice == '5':
            modify_booking_from_console(db_name)
        elif choice == '6':
            modify_user_from_console(db_name)
        elif choice == '0':
            print("\nЗавершение работы.")
            break
        else:
            print("Некорректный ввод. Пожалуйста, выберите число от 0 до 6.")

# Пример запуска (для проверки):
if __name__ == '__main__':
    DB_NAME = "coaching.db"
    
    # Создаем таблицы
    create_tables(DB_NAME)
    print(f"\n✅ Таблицы созданы в '{DB_NAME}'.")
    
    # Вставляем данные
    insert_sample_data(DB_NAME)

    # ----------------------------------------------------
    # Запускаем главное меню
    main_menu(DB_NAME)
    # ----------------------------------------------------

    # Проверяем, что данные были добавлены (опционально)
    conn = get_connection(DB_NAME)
    cursor = conn.cursor()
    
    # Проверка бронирований
    conn = get_connection(DB_NAME)
    print("\n--- Финальный список всех бронирований ---")
    display_all_bookings_details(conn)
    conn.close()