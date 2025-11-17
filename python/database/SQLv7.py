import sqlite3
from sqlite3 import Connection
from datetime import datetime
from typing import Dict, Tuple, Callable, List, Any
import sys
import json
import csv
import os
import yaml
import xml.etree.ElementTree as ET

# =================================================================
# === 1. УПРАВЛЕНИЕ БД: СОЕДИНЕНИЕ, СТРУКТУРА И ДАННЫЕ (Utility) ===
# =================================================================

def get_connection(db_name: str = "coaching.db") -> Connection:
    """Создает соединение с базой данных SQLite с поддержкой внешних ключей."""
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(db_name: str = "coaching.db"):
    """
    Создает таблицы: Coach, User, Inventory, Status, Booking, Booking_inventory.
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()

    # 1. Таблица Coach
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Coach (
            Coach_ID INTEGER PRIMARY KEY,
            Internal_number INTEGER UNIQUE NOT NULL, 
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
    print("Таблицы созданы.")


def insert_sample_data(db_name: str = "coaching.db"):
    """
    Вставляет тестовые записи, включая профиль Администратора (Internal_number 999).
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    # Проверка, что данные не были вставлены ранее (по наличию Админа)
    cursor.execute("SELECT COUNT(*) FROM Coach WHERE Internal_number = 999")
    if cursor.fetchone()[0] > 0:
        print("Тестовые данные (включая Администратора) уже существуют. Пропускаем вставку.")
        conn.close()
        return

    # Вставка Администратора: Логин 'admin', Internal_number 999, Пароль 'admin_pass'
    cursor.execute("""
    INSERT INTO Coach (Internal_number, Surname, Name, Experience, Password)
    VALUES (?, ?, ?, ?, ?)
    """, (999, "Системный", "Администратор", 99, "admin_pass"))
    
    # Вставка Тренера: Логин '101', Пароль 'pass101'
    coaches = [
        (101, "Иванов", "Петр", 5, "pass101"),
        (102, "Сидорова", "Мария", 8, "pass102")
    ]
    cursor.executemany("INSERT INTO Coach (Internal_number, Surname, Name, Experience, Password) VALUES (?, ?, ?, ?, ?)", coaches)

    # Вставка Пользователя: Логин '1' (User_ID), Пароль 'userpass1'
    users = [
        ("Климов", "Алексей", "userpass1"),
        ("Орлова", "Елена", "userpass2")
    ]
    cursor.executemany("INSERT INTO User (Surname, Name, Password) VALUES (?, ?, ?)", users)
    
    # Вставка статусов для Booking_inventory
    statuses = [
        ("Забронировано", "Ожидает подтверждения"),
        ("Подтверждено", "Бронирование активно"),
        ("Отменено", "Бронирование отменено пользователем"),
        ("Завершено", "Услуга оказана")
    ]
    cursor.executemany("INSERT INTO Status (Name, Comment) VALUES (?, ?)", statuses)
    
    # Вставка инвентаря
    inventory_items = [
        ("Мяч для фитнеса", 5, "Стандартный диаметр"),
        ("Коврик для йоги", 10, "С противоскользящим покрытием"),
        ("Гантели 5кг", 2, "Пара")
    ]
    cursor.executemany("INSERT INTO Inventory (Name, Count, Comment) VALUES (?, ?, ?)", inventory_items)
    
    # Вставка тестовых бронирований
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    future = datetime(2025, 12, 10, 15, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    
    bookings = [
        (1, 1, now, future, 1), # Coach_ID 1 (Админ, хотя лучше бы 2), User_ID 1
        (2, 2, now, future, 2)  # Coach_ID 2, User_ID 2
    ]
    cursor.executemany("INSERT INTO Booking (Coach_ID, User_ID, Time_start, Time_end, Number_booking) VALUES (?, ?, ?, ?, ?)", bookings)
    
    # Вставка связей бронирования с инвентарем
    # Booking_ID 1: Inventory 1 (Мяч), Status 2 (Подтверждено)
    # Booking_ID 2: Inventory 3 (Гантели), Status 1 (Забронировано)
    booking_inventories = [
        (1, 1, 2), 
        (3, 2, 1) 
    ]
    cursor.executemany("INSERT INTO Booking_inventory (Inventory_ID, Booking_ID, Status_ID) VALUES (?, ?, ?)", booking_inventories)

    conn.commit()
    conn.close()
    print("✅ Тестовые данные успешно вставлены.")

# =================================================================
# === 2. ФУНКЦИИ ПРОСМОТРА (Utility) ===
# =================================================================

def indent(elem, level=0):
    """
    Добавляет отступы (пробелы) к XML-элементам для "красивого" вывода (pretty-print).
    """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
            
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
    print("| Booking_ID | Start Time           | End Time             | User        | Coach       | Inventory | Status    |")
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
    print("| User_ID | Фамилия   | Имя         | Пароль   |")
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
    print("| Inventory_ID | Название              | Кол-во | Комментарий     |")
    print("=================================================================")
    for row in inventory:
        comment_display = row[3] if row[3] else '---'
        print(f"| {row[0]:<12} | {row[1]:<19} | {row[2]:<6} | {comment_display:<15} |")
    print("=================================================================")
    return True

# =================================================================
# === 3. ФУНКЦИИ УПРАВЛЕНИЯ ДАННЫМИ (CRUD) ===
# =================================================================

# --- ADD ---

def add_inventory_from_console(db_name: str = "coaching.db"):
    """Добавляет новый инвентарь в таблицу Inventory."""
    conn = get_connection(db_name)
    cursor = conn.cursor()
    print("\n--- Добавление нового Инвентаря ---")
    try:
        # Отобразим текущий инвентарь для справки
        display_all_inventory_details(conn)
        
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
    except sqlite3.IntegrityError:
        print("❌ Ошибка: Внутренний номер уже существует.")
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
        # Ввод времени (должен быть в формате SQLite TEXT, например, YYYY-MM-DD HH:MM:SS)
        time_start_str = input("Введите время начала (YYYY-MM-DD HH:MM:SS): ")
        time_end_str = input("Введите время окончания (YYYY-MM-DD HH:MM:SS): ")
        
        # Генерация Number_booking
        cursor.execute("SELECT IFNULL(MAX(Number_booking), 0) FROM Booking")
        next_booking_number = cursor.fetchone()[0] + 1
        
        # 1. Добавление в Booking
        cursor.execute(
            "INSERT INTO Booking (Coach_ID, User_ID, Time_start, Time_end, Number_booking) VALUES (?, ?, ?, ?, ?)",
            (coach_id, user_id, time_start_str, time_end_str, next_booking_number)
        )
        booking_id = cursor.lastrowid
        
        print(f"\nБронирование успешно добавлено. Booking_ID: {booking_id}")

        inventory_id = int(input("Введите ID Инвентаря (Inventory_ID) для бронирования: "))
        status_id = int(input("Введите ID Статуса (Status_ID) для этого инвентаря: "))

        # 2. Добавление в Booking_inventory
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

# --- MODIFY ---

def modify_booking_from_console(db_name: str = "coaching.db"):
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    print("\n--- Изменение существующего бронирования (Booking) ---")
    
    if not display_all_bookings_details(conn):
        conn.close()
        return

    try:
        booking_id = int(input("\nВведите ID Бронирования (Booking_ID) для изменения: "))
        
        cursor.execute("SELECT Coach_ID, User_ID, Time_start, Time_end FROM Booking WHERE Booking_ID = ?", (booking_id,))
        booking_record = cursor.fetchone()
        
        if not booking_record:
            print(f"❌ Ошибка: Бронирование с ID {booking_id} не найдено.")
            conn.close()
            return
            
        print(f"\n--- Изменение записи Booking_ID: {booking_id} ---")

        print("Введите новое значение или оставьте поле пустым, чтобы не менять.")
        new_coach_id = input(f"Новый ID Тренера (текущий: {booking_record[0]}): ")
        new_user_id = input(f"Новый ID Пользователя (текущий: {booking_record[1]}): ")
        new_time_start = input(f"Новое время начала (текущее: {booking_record[2]}): ")
        new_time_end = input(f"Новое время окончания (текущее: {booking_record[3]}): ")

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
            
        # Обновление Booking_inventory
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
    Позволяет выбрать элемент инвентаря по ID и изменить его.
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    print("\n--- Изменение данных Инвентаря (Inventory) ---")
    
    if not display_all_inventory_details(conn):
        conn.close()
        return

    try:
        inventory_id = int(input("\nВведите ID Инвентаря (Inventory_ID) для изменения: "))
        
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
            new_count = int(new_count_str) 
            update_fields.append("Count = ?")
            params.append(new_count)
            
        # Устанавливаем NULL, если пользователь ввел пустую строку для комментария
        if new_comment:
            update_fields.append("Comment = ?")
            params.append(new_comment)
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


OUTPUT_DIR = "out" # <-- Добавить это

def ensure_output_directory(path: str): # <-- Добавить это
    """Создает директорию для экспорта, если она еще не существует."""
    os.makedirs(path, exist_ok=True)


def export_table_to_file(db_name: str):
    """Универсальный экспорт одной таблицы в JSON, CSV, YAML или XML."""
    
    print("\n--- Универсальный экспорт таблицы ---")
    
    table_name = input("Введите имя таблицы (User, Coach, Inventory): ")
    if not table_name: return
    
    file_format = input("Выберите формат (json / csv / yaml / xml): ").lower() # <-- Обновлено
    if file_format not in ['json', 'csv', 'yaml', 'xml']: # <-- Обновлено
        print("❌ Неподдерживаемый формат. Выберите 'json', 'csv', 'yaml' или 'xml'."); return

    output_filename = f"{table_name.lower()}.{file_format}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    ensure_output_directory(OUTPUT_DIR)

    conn = None
    try:
        conn = get_connection(db_name)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        sql_query = f"SELECT * FROM {table_name}" 
        cursor.execute(sql_query)
        
        column_names = [description[0] for description in cursor.description]
        records = cursor.fetchall()

        if not records:
            print(f"ℹ️ Таблица '{table_name}' пуста или не существует."); return
            
        # Преобразование в список словарей для универсальности экспорта
        data_to_export = [dict(row) for row in records]

        if file_format == 'json':
            # Сериализация в JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_export, f, ensure_ascii=False, indent=4)
            print(f"✅ Плоский экспорт '{table_name}' (JSON) завершен. Файл: {output_path}")

        elif file_format == 'csv':
            # Сериализация в CSV (с использованием заголовков и разделителя ;)
            # ... (Оставить вашу существующую логику CSV) ...
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                csv_writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(column_names)
                # records все еще доступны как Row объекты/кортежи
                csv_writer.writerows(records) 
            print(f"✅ Плоский экспорт '{table_name}' (CSV) завершен. Файл: {output_path}")

        elif file_format == 'yaml':
            # Сериализация в YAML
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data_to_export, f, allow_unicode=True, indent=4, sort_keys=False) # sort_keys=False сохраняет порядок
            print(f"✅ Плоский экспорт '{table_name}' (YAML) завершен. Файл: {output_path}")

        elif file_format == 'xml':
            # Сериализация в XML с использованием ElementTree
            root = ET.Element(table_name)
            for item in data_to_export:
                record_element = ET.SubElement(root, table_name[:-1] if table_name.endswith('s') else "record") # Используем 'record' или форму единственного числа
                for key, value in item.items():
                    field_element = ET.SubElement(record_element, key)
                    field_element.text = str(value)
            
            tree = ET.ElementTree(root)
            with open(output_path, 'wb') as f: # Используем 'wb' для записи байтов, так как ET.write требует этого
                tree.write(f, encoding='utf-8', xml_declaration=True)
                
            print(f"✅ Плоский экспорт '{table_name}' (XML) завершен. Файл: {output_path}")


    except sqlite3.OperationalError as e:
        print(f"❌ Ошибка SQL: Таблицы '{table_name}' не существует. ({e})")
    except ImportError:
        print("❌ Ошибка: Библиотека PyYAML не установлена. Пожалуйста, установите ее (pip install pyyaml).")
    except Exception as e:
        print(f"❌ Произошла ошибка при экспорте: {e}")
    finally:
        if conn: conn.close()


def export_nested_booking_to_file(db_name: str):
    """
    Извлекает данные о бронированиях с вложенной информацией 
    о Тренере, Пользователе и Инвентаре и экспортирует их в JSON, YAML или XML.
    """
    
    print("\n--- Вложенный экспорт бронирований ---")
    
    file_format = input("Выберите формат (json / yaml / xml): ").lower()
    if file_format not in ['json', 'yaml', 'xml']:
        print("❌ Неподдерживаемый формат. Выберите 'json', 'yaml' или 'xml'."); return

    output_filename = f"bookings_nested_export.{file_format}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    ensure_output_directory(OUTPUT_DIR)

    conn = None
    try:
        conn = get_connection(db_name)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        # 1. Получение основных данных бронирований (то же, что и ранее)
        cursor.execute("""
            SELECT 
                B.Booking_ID, B.Time_start, B.Time_end, B.Number_booking,
                C.Coach_ID, C.Internal_number, C.Surname AS Coach_Surname, C.Name AS Coach_Name,
                U.User_ID, U.Surname AS User_Surname, U.Name AS User_Name
            FROM Booking B
            JOIN Coach C ON B.Coach_ID = C.Coach_ID
            JOIN User U ON B.User_ID = U.User_ID
            ORDER BY B.Booking_ID
        """)
        main_bookings = [dict(row) for row in cursor.fetchall()]

        if not main_bookings: print("ℹ️ Таблица 'Booking' пуста."); return

        bookings_dict = {}
        for row in main_bookings:
            booking_id = row['Booking_ID']
            coach_details = {'id': row.pop('Coach_ID'), 'internal_number': row.pop('Internal_number'), 'surname': row.pop('Coach_Surname'), 'name': row.pop('Coach_Name')}
            user_details = {'id': row.pop('User_ID'), 'surname': row.pop('User_Surname'), 'name': row.pop('User_Name')}
            
            bookings_dict[booking_id] = {
                'id': row.pop('Booking_ID'), 'number': row.pop('Number_booking'),
                'time_start': row.pop('Time_start'), 'time_end': row.pop('Time_end'),
                'coach': coach_details, 
                'user': user_details, 
                'inventory_items': []
            }

        # 2. Получение деталей инвентаря и вложение (то же, что и ранее)
        cursor.execute("""
            SELECT BI.Booking_ID, I.Inventory_ID, I.Name AS Inventory_Name, I.Count, S.Status_ID, S.Name AS Status_Name
            FROM Booking_inventory BI
            JOIN Inventory I ON BI.Inventory_ID = I.Inventory_ID
            JOIN Status S ON BI.Status_ID = S.Status_ID
        """)
        inventory_records = [dict(row) for row in cursor.fetchall()]

        for row in inventory_records:
            booking_id = row.pop('Booking_ID')
            if booking_id in bookings_dict:
                item_details = {
                    'inventory_id': row.pop('Inventory_ID'), 'name': row.pop('Inventory_Name'),
                    'count_available': row.pop('Count'),
                    'status': {'status_id': row.pop('Status_ID'), 'name': row.pop('Status_Name')}
                }
                bookings_dict[booking_id]['inventory_items'].append(item_details)

        final_records = list(bookings_dict.values())
        
        # 3. Сохранение в выбранный файл
        if file_format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_records, f, ensure_ascii=False, indent=4)
        
        elif file_format == 'yaml':
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(final_records, f, allow_unicode=True, indent=4, sort_keys=False)

        elif file_format == 'xml':
            # Вспомогательная функция для рекурсивного создания XML
            def dict_to_xml(tag, d):
                # ... (Ваша реализация dict_to_xml)
                elem = ET.Element(tag)
                # ... (логика заполнения элементов)
                return elem # <--- Убедитесь, что тут есть return

            root = ET.Element("bookings")
            for booking in final_records:
                # 1. Создание и добавление элемента booking
                root.append(dict_to_xml("booking", booking))
                
            
            # 2. ❗ КРИТИЧЕСКИЙ ШАГ: Вызываем функцию форматирования
            indent(root) 
            
            tree = ET.ElementTree(root)
            with open(output_path, 'wb') as f: 
                # 3. Запись дерева в файл
                tree.write(f, encoding='utf-8', xml_declaration=True)
                
            print(f"✅ Вложенный экспорт бронирований (XML) завершен. Файл: {output_path}")

            root = ET.Element("bookings")
            for booking in final_records:
                root.append(dict_to_xml("booking", booking))
                
            tree = ET.ElementTree(root)
            # Используем 'wb' для записи байтов
            with open(output_path, 'wb') as f:
                tree.write(f, encoding='utf-8', xml_declaration=True)

        print(f"✅ Вложенный экспорт бронирований ({file_format.upper()}) завершен. Файл: {output_path}")

    except Exception as e:
        print(f"❌ Произошла ошибка при вложенном экспорте: {e}")
    finally:
        if conn: conn.close()
        
# =================================================================
# === 5. КАРТА ДЕЙСТВИЙ И ПОЛИТИКА РОЛЕЙ (ОСНОВА ДИНАМИЧЕСКОГО МЕНЮ) ===
# =================================================================

ACTION_MAP: Dict[str, Tuple[str, Callable]] = {
    "ADD_COACH": ("Добавить нового Тренера", add_coach_from_console),
    "ADD_USER": ("Добавить нового Пользователя", add_user_from_console),
    "MODIFY_USER": ("Изменить данные Пользователя", modify_user_from_console),
    "ADD_INVENTORY": ("Добавить Инвентарь", add_inventory_from_console),
    "MODIFY_INVENTORY": ("Изменить данные Инвентаря", modify_inventory_from_console),
    "ADD_BOOKING": ("Добавить новое Бронирование", add_booking_from_console),
    "MODIFY_BOOKING": ("Изменить существующее Бронирование", modify_booking_from_console),
    "EXPORT_FLAT": ("Экспорт таблицы (плоский JSON/CSV/YAML/XML)", export_table_to_file),
    "EXPORT_NESTED": ("Экспорт Бронирований (вложенный JSON/YAML/XML)", export_nested_booking_to_file),
}

ROLE_POLICY: Dict[str, List[str]] = {
    "Администратор": [
        "ADD_COACH", "ADD_USER", "MODIFY_USER", 
        "ADD_INVENTORY", "MODIFY_INVENTORY", 
        "ADD_BOOKING", "MODIFY_BOOKING", 
        "EXPORT_FLAT", "EXPORT_NESTED"
    ],
    "Тренер": [
        "ADD_BOOKING", "MODIFY_BOOKING"
    ],
    "Пользователь": [
        "ADD_BOOKING",
    ]
}

# =================================================================
# === 6. АУТЕНТИФИКАЦИЯ И МЕНЮ ===
# =================================================================

def authenticate_user(db_name: str, username: str, password: str) -> str | None:
    conn = get_connection(db_name)
    cursor = conn.cursor()
    role = None
    try:
        if username.lower() == 'admin':
            cursor.execute("SELECT Coach_ID FROM Coach WHERE Internal_number = 999 AND Password = ?", (password,))
            if cursor.fetchone(): role = "Администратор"
        elif not role:
            try:
                internal_number = int(username)
                cursor.execute("SELECT Coach_ID FROM Coach WHERE Internal_number = ? AND Password = ?", (internal_number, password))
                if cursor.fetchone(): role = "Тренер"
            except ValueError: pass 
        if not role:
            try:
                user_id = int(username)
                cursor.execute("SELECT User_ID FROM User WHERE User_ID = ? AND Password = ?", (user_id, password))
                if cursor.fetchone(): role = "Пользователь"
            except ValueError: pass 
    except Exception as e: print(f"❌ Ошибка БД при аутентификации: {e}")
    finally: conn.close()
    return role


def main_menu(db_name: str, current_user_role: str):
    if current_user_role not in ROLE_POLICY: print("Ошибка: Неизвестная роль."); return

    allowed_action_keys = ROLE_POLICY[current_user_role]
    current_menu_actions = {}
    i = 1
    
    for action_key in allowed_action_keys:
        if action_key in ACTION_MAP:
            current_menu_actions[str(i)] = ACTION_MAP[action_key]
            i += 1
    
    while True:
        print("\n" + "="*40)
        print(f" 💻 МЕНЮ: {current_user_role.upper()}")
        print("="*40)
        for key, (description, _) in current_menu_actions.items(): print(f"{key}. {description}") 
        print("0. Выход/Смена пользователя")
        print("="*40)
        
        choice = input("Выберите действие: ")
        
        if choice == '0':
            print(f"\nВыход из системы. До свидания!"); break
        elif choice in current_menu_actions:
            function_to_call = current_menu_actions[choice][1]
            function_to_call(db_name) 
        else:
            print("Некорректный ввод. Пожалуйста, выберите номер из списка.")


def start_program(db_name: str = "coaching.db"):
    while True:
        print("\n" + "="*40)
        print(" 🏋️ СИСТЕМА УПРАВЛЕНИЯ КОУЧИНГОМ")
        print("="*40)
        print("Подсказки для входа:")
        print(" - **Админ**: Логин=admin, Пароль=admin_pass")
        print(" - Тренер (Сидорова): Логин=102, Пароль=pass102")
        print(" - Пользователь (Климов): Логин=1, Пароль=userpass1")
        
        username = input("Введите Логин: ")
        password = input("Введите Пароль: ")
        
        current_user_role = authenticate_user(db_name, username, password)
        
        if current_user_role:
            print(f"✅ Успешный вход! Ваша роль: **{current_user_role}**.")
            main_menu(db_name, current_user_role)
        else:
            print("❌ Ошибка аутентификации. Неверный логин или пароль.")
        
        continue_choice = input("Хотите попробовать войти снова? (д/н): ").lower()
        if continue_choice != 'д':
            print("\nЗавершение программы.")
            sys.exit() 


# =================================================================
# === 7. ТОЧКА ЗАПУСКА ===
# =================================================================

if __name__ == '__main__':
    DB_NAME = "coaching.db"
    
    try:
        create_tables(DB_NAME)
        insert_sample_data(DB_NAME)
        start_program(DB_NAME)
        
    except Exception as e:
        print(f"Критическая ошибка программы: {e}")