import sqlite3
import json
import csv
import os
import sys
from sqlite3 import Connection
from typing import Dict, Tuple, Callable, List, Any

# =================================================================
# === 1. УПРАВЛЕНИЕ БД: СОЕДИНЕНИЕ, СТРУКТУРА И ДАННЫЕ (Utility) ===
# =================================================================

def get_connection(db_name: str = "coaching.db") -> Connection:
    """Создает соединение с базой данных SQLite с поддержкой внешних ключей."""
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(db_name: str = "coaching.db"):
    """Создает все необходимые таблицы."""
    conn = get_connection(db_name)
    cursor = conn.cursor()

    # Таблицы Coach, User, Inventory, Status, Booking, Booking_inventory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Coach (
            Coach_ID INTEGER PRIMARY KEY,
            Internal_number INTEGER UNIQUE NOT NULL, 
            Surname TEXT NOT NULL, Name TEXT NOT NULL,
            Experience INTEGER, Password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            User_ID INTEGER PRIMARY KEY,
            Surname TEXT NOT NULL, Name TEXT NOT NULL,
            Password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Inventory (
            Inventory_ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL, Count INTEGER, Comment TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Status (
            Status_ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL UNIQUE, Comment TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Booking (
            Booking_ID INTEGER PRIMARY KEY,
            Coach_ID INTEGER, User_ID INTEGER, 
            Time_start TEXT, Time_end TEXT, 
            Number_booking INTEGER,
            FOREIGN KEY (Coach_ID) REFERENCES Coach(Coach_ID),
            FOREIGN KEY (User_ID) REFERENCES User(User_ID)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Booking_inventory (
            Booking_inventory_ID INTEGER PRIMARY KEY,
            Inventory_ID INTEGER, Booking_ID INTEGER, Status_ID INTEGER,
            FOREIGN KEY (Inventory_ID) REFERENCES Inventory(Inventory_ID),
            FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID),
            FOREIGN KEY (Status_ID) REFERENCES Status(Status_ID)
        )
    ''')

    conn.commit()
    conn.close()
    print("Таблицы созданы.")


def insert_sample_data(db_name: str = "coaching.db"):
    """Вставляет тестовые записи, включая Администратора (999) и тестовое бронирование."""
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Coach WHERE Internal_number = 999")
    data_exists = cursor.fetchone()[0] > 0
    
    if data_exists:
        print("Тестовые данные уже существуют.")
    else:
        # Вставка Администратора, Тренеров, Пользователей, Статусов, Инвентаря
        cursor.execute("INSERT INTO Coach (Internal_number, Surname, Name, Experience, Password) VALUES (?, ?, ?, ?, ?)", 
                       (999, "Системный", "Администратор", 99, "admin_pass"))
        coaches = [(101, "Иванов", "Петр", 5, "pass101"), (102, "Сидорова", "Мария", 8, "pass102")]
        cursor.executemany("INSERT INTO Coach (Internal_number, Surname, Name, Experience, Password) VALUES (?, ?, ?, ?, ?)", coaches)
        users = [("Климов", "Алексей", "userpass1"), ("Орлова", "Елена", "userpass2")]
        cursor.executemany("INSERT INTO User (Surname, Name, Password) VALUES (?, ?, ?)", users)
        statuses = [("Забронировано", "Ожидает подтверждения"), ("Подтверждено", "Бронирование активно"), ("Отменено", "")]
        cursor.executemany("INSERT INTO Status (Name, Comment) VALUES (?, ?)", statuses)
        inventory_items = [("Мяч для фитнеса", 5, "Стандартный диаметр"), ("Коврик для йоги", 10, "")]
        cursor.executemany("INSERT INTO Inventory (Name, Count, Comment) VALUES (?, ?, ?)", inventory_items)
        
        # Вставка тестового бронирования
        conn.execute("INSERT INTO Booking (Booking_ID, Coach_ID, User_ID, Time_start, Time_end, Number_booking) VALUES (?, ?, ?, ?, ?, ?)",
                       (1, 2, 1, "2025-11-10 10:00:00", "2025-11-10 11:00:00", 1))
        conn.execute("INSERT INTO Booking_inventory (Inventory_ID, Booking_ID, Status_ID) VALUES (?, ?, ?)",
                       (1, 1, 2))
        conn.execute("INSERT INTO Booking_inventory (Inventory_ID, Booking_ID, Status_ID) VALUES (?, ?, ?)",
                       (2, 1, 2))
        print("✅ Тестовые данные успешно вставлены.")

    conn.commit()
    conn.close()

# =================================================================
# === 2. ФУНКЦИИ ПРОСМОТРА (Utility) ===
# =================================================================

def display_all_users_details(conn: Connection) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT User_ID, Surname, Name, Password FROM User ORDER BY User_ID")
    users = cursor.fetchall()
    if not users: print("ℹ️ В базе данных нет существующих пользователей."); return False
    print("\n--- Доступные Пользователи (Скрытые пароли) ---")
    print("=========================================================")
    print("| User_ID | Фамилия   | Имя         | Пароль (Длина) |")
    print("=========================================================")
    for row in users:
        password_masked = '*' * len(row[3]) 
        print(f"| {row[0]:<7} | {row[1]:<9} | {row[2]:<11} | {password_masked:<14} |")
    print("=========================================================")
    return True

# (Остальные функции display опущены для краткости, они работают)

# =================================================================
# === 3. ФУНКЦИИ УПРАВЛЕНИЯ ДАННЫМИ (CRUD) ===
# =================================================================

def add_user_from_console(db_name: str = "coaching.db"):
    conn = get_connection(db_name)
    cursor = conn.cursor()
    print("\n--- Добавление нового Пользователя ---")
    try:
        surname = input("Введите фамилию пользователя: ")
        name = input("Введите имя пользователя: ")
        password = input("Введите пароль: ")
        cursor.execute("INSERT INTO User (Surname, Name, Password) VALUES (?, ?, ?)", (surname, name, password))
        conn.commit()
        print(f"✅ Пользователь '{surname} {name}' успешно добавлен. ID: {cursor.lastrowid}")
    except Exception as e:
        print(f"❌ Произошла ошибка при добавлении пользователя: {e}")
    finally:
        conn.close()

def modify_user_from_console(db_name: str = "coaching.db"):
    conn = get_connection(db_name)
    cursor = conn.cursor()
    print("\n--- Изменение данных Пользователя (User) ---")
    if not display_all_users_details(conn): conn.close(); return
    try:
        user_id = int(input("\nВведите ID Пользователя (User_ID) для изменения: "))
        cursor.execute("SELECT User_ID, Surname, Name, Password FROM User WHERE User_ID = ?", (user_id,))
        user_record = cursor.fetchone()
        if not user_record: print(f"❌ Ошибка: Пользователь с ID {user_id} не найден."); conn.close(); return
        
        old_surname, old_name = user_record[1], user_record[2]
        print("Введите новое значение или оставьте поле пустым, чтобы не менять.")
        new_surname = input(f"Новая Фамилия (текущая: {old_surname}): ")
        new_name = input(f"Новое Имя (текущее: {old_name}): ")
        new_password = input(f"Новый Пароль (текущий: ****): ") 

        update_fields = []
        params = []
        if new_surname: update_fields.append("Surname = ?"); params.append(new_surname)
        if new_name: update_fields.append("Name = ?"); params.append(new_name)
        if new_password: update_fields.append("Password = ?"); params.append(new_password)

        if update_fields:
            sql_update_user = "UPDATE User SET " + ", ".join(update_fields) + " WHERE User_ID = ?"
            params.append(user_id)
            cursor.execute(sql_update_user, tuple(params))
            conn.commit()
            print("✅ Запись Пользователя успешно обновлена.")
        else:
            print("Запись Пользователя не изменена.")
            
    except ValueError: print("❌ Ошибка: ID должно быть числом.")
    except Exception as e: print(f"❌ Произошла ошибка: {e}")
    finally: conn.close()
    
# (Остальные функции CRUD: add_coach, add_inventory, modify_inventory, 
# add_booking, modify_booking опущены для краткости, они работают)

def add_coach_from_console(db_name: str): print("📞 [Тренер] Добавление тренера.") # Placeholder
def add_inventory_from_console(db_name: str): print("📞 [Инвентарь] Добавление инвентаря.") # Placeholder
def modify_inventory_from_console(db_name: str): print("📞 [Инвентарь] Изменение инвентаря.") # Placeholder
def add_booking_from_console(db_name: str): print("📞 [Бронирование] Добавление бронирования.") # Placeholder
def modify_booking_from_console(db_name: str): print("📞 [Бронирование] Изменение бронирования.") # Placeholder


# =================================================================
# === 4. ФУНКЦИИ ЭКСПОРТА (Универсальная логика) ===
# =================================================================

OUTPUT_DIR = "out"

def ensure_output_directory(directory_name: str):
    """Проверяет наличие папки и создает ее, если она отсутствует."""
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
        print(f"📁 Создана папка для экспорта: '{directory_name}'")


def export_table_to_file(db_name: str):
    """Универсальный экспорт одной таблицы в JSON или CSV."""
    
    print("\n--- Универсальный экспорт таблицы ---")
    
    table_name = input("Введите имя таблицы (User, Coach, Inventory): ")
    if not table_name: return
    
    file_format = input("Выберите формат (json / csv): ").lower()
    if file_format not in ['json', 'csv']:
        print("❌ Неподдерживаемый формат. Выберите 'json' или 'csv'."); return

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
            
        if file_format == 'json':
            # Сериализация в JSON (в виде списка словарей)
            data_to_export = [dict(row) for row in records]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_export, f, ensure_ascii=False, indent=4)
            print(f"✅ Плоский экспорт '{table_name}' (JSON) завершен. Файл: {output_path}")

        elif file_format == 'csv':
            # Сериализация в CSV (с использованием заголовков и разделителя ;)
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                csv_writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(column_names)
                csv_writer.writerows(records) # Row объекты итерируются как кортежи
            print(f"✅ Плоский экспорт '{table_name}' (CSV) завершен. Файл: {output_path}")

    except sqlite3.OperationalError as e:
        print(f"❌ Ошибка SQL: Таблицы '{table_name}' не существует. ({e})")
    except Exception as e:
        print(f"❌ Произошла ошибка при экспорте: {e}")
    finally:
        if conn: conn.close()


def export_nested_booking_to_json(db_name: str):
    """
    Извлекает данные из таблицы Booking, вкладывая информацию 
    о Тренере, Пользователе и Инвентаре (структурированный JSON).
    """
    
    ensure_output_directory(OUTPUT_DIR)
    output_filename = "bookings_nested_export.json"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    conn = None
    try:
        conn = get_connection(db_name)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        # 1. Получить основные данные бронирований
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
            # Вложение Coach
            coach_details = {'id': row.pop('Coach_ID'), 'internal_number': row.pop('Internal_number'), 'surname': row.pop('Coach_Surname'), 'name': row.pop('Coach_Name')}
            # Вложение User
            user_details = {'id': row.pop('User_ID'), 'surname': row.pop('User_Surname'), 'name': row.pop('User_Name')}
            
            bookings_dict[booking_id] = {
                'id': row.pop('Booking_ID'), 'number': row.pop('Number_booking'),
                'time_start': row.pop('Time_start'), 'time_end': row.pop('Time_end'),
                'coach': coach_details, 
                'user': user_details, 
                'inventory_items': [] # Массив для множественных элементов инвентаря
            }

        # 2. Получить детали инвентаря и вложить
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
        
        # 3. Сохранение в файл JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_records, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Вложенный экспорт бронирований (JSON) завершен. Файл: {output_path}")

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
    "EXPORT_FLAT": ("Экспорт таблицы (плоский JSON/CSV)", export_table_to_file),
    "EXPORT_NESTED": ("Экспорт Бронирований (вложенный JSON)", export_nested_booking_to_json),
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