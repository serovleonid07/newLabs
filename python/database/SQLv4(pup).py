import sqlite3
from sqlite3 import Connection
from datetime import datetime
from typing import Dict, Tuple, Callable, List
import sys # Для sys.exit()

# =================================================================
# === 1. КАРТА ДЕЙСТВИЙ И ПОЛИТИКА РОЛЕЙ (ОСНОВА ДИНАМИЧЕСКОГО МЕНЮ) ===
# =================================================================

# Здесь должны быть объявления всех функций, которые вызываются из меню.
# Временно используем заглушки.
def add_coach_from_console(db_name: str): print(f"📞 [Тренер] Вызвана функция добавления тренера.")
def add_user_from_console(db_name: str): print(f"📞 [Пользователь] Вызвана функция добавления пользователя.")
def modify_user_from_console(db_name: str): print(f"📞 [Пользователь] Вызвана функция изменения данных пользователя.")
def add_inventory_from_console(db_name: str): print(f"📞 [Инвентарь] Вызвана функция добавления инвентаря.")
def modify_inventory_from_console(db_name: str): print(f"📞 [Инвентарь] Вызвана функция изменения данных инвентаря.")
def add_booking_from_console(db_name: str): print(f"📞 [Бронирование] Вызвана функция добавления бронирования.")
def modify_booking_from_console(db_name: str): print(f"📞 [Бронирование] Вызвана функция изменения бронирования.")
# Дополнительные заглушки для полноты системы, если они нужны:
def display_all_inventory_details(db_name: str): print(f"📞 [Просмотр] Вызвана функция просмотра инвентаря.")


ACTION_MAP: Dict[str, Tuple[str, Callable]] = {
    # (Описание в меню, Функция для вызова)
    "ADD_COACH": ("1. Добавить нового Тренера", add_coach_from_console),
    "ADD_USER": ("2. Добавить нового Пользователя", add_user_from_console),
    "MODIFY_USER": ("3. Изменить данные Пользователя", modify_user_from_console),
    "ADD_INVENTORY": ("4. Добавить Инвентарь", add_inventory_from_console),
    "MODIFY_INVENTORY": ("5. Изменить данные Инвентаря", modify_inventory_from_console),
    "ADD_BOOKING": ("6. Добавить новое Бронирование", add_booking_from_console),
    "MODIFY_BOOKING": ("7. Изменить существующее Бронирование", modify_booking_from_console),
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

# =================================================================
# === 2. УПРАВЛЕНИЕ БД: СОЕДИНЕНИЕ, СТРУКТУРА И ДАННЫЕ ===
# =================================================================

def get_connection(db_name: str = "coaching.db") -> Connection:
    """Создает соединение с БД с поддержкой внешних ключей."""
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(db_name: str = "coaching.db"):
    """Создает таблицы Coach, User, Inventory, Status, Booking, Booking_inventory с полем Password."""
    conn = get_connection(db_name)
    cursor = conn.cursor()

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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            User_ID INTEGER PRIMARY KEY,
            Surname TEXT NOT NULL,
            Name TEXT NOT NULL,
            Password TEXT NOT NULL
        )
    ''')
    
    # ... (Остальные таблицы Inventory, Status, Booking, Booking_inventory должны быть здесь)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Inventory (Inventory_ID INTEGER PRIMARY KEY, Name TEXT NOT NULL, Count INTEGER, Comment TEXT)
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Status (Status_ID INTEGER PRIMARY KEY, Name TEXT NOT NULL UNIQUE, Comment TEXT)
    ''')
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
    """Вставляет тестовые данные, включая профиль Администратора (Internal_number 999)."""
    conn = get_connection(db_name)
    cursor = conn.cursor()
    
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
    cursor.execute("""
    INSERT INTO Coach (Internal_number, Surname, Name, Experience, Password)
    VALUES (?, ?, ?, ?, ?)
    """, (101, "Иванов", "Петр", 5, "pass101"))
    
    # Вставка Пользователя: Логин '1' (User_ID), Пароль 'userpass1'
    cursor.execute("""
    INSERT INTO User (Surname, Name, Password)
    VALUES (?, ?, ?)
    """, ("Климов", "Алексей", "userpass1"))
    
    # Вставка статусов для Booking_inventory
    statuses = [("Забронировано", ""), ("Подтверждено", ""), ("Отменено", "")]
    cursor.executemany("INSERT INTO Status (Name, Comment) VALUES (?, ?)", statuses)
    
    conn.commit()
    conn.close()
    print("✅ Тестовые данные успешно вставлены.")

# =================================================================
# === 3. АУТЕНТИФИКАЦИЯ И МЕНЮ (Ядро вашей логики) ===
# =================================================================

def authenticate_user(db_name: str, username: str, password: str) -> str | None:
    """Проверяет логин/пароль и возвращает роль."""
    conn = get_connection(db_name)
    cursor = conn.cursor()
    role = None
    
    try:
        # 1. Администратор (логин: 'admin', Internal_number 999)
        if username.lower() == 'admin':
            cursor.execute("SELECT Coach_ID FROM Coach WHERE Internal_number = 999 AND Password = ?", (password,))
            if cursor.fetchone():
                role = "Администратор"
                
        # 2. Тренер (логин: Internal_number)
        elif not role:
            try:
                internal_number = int(username)
                cursor.execute("SELECT Coach_ID FROM Coach WHERE Internal_number = ? AND Password = ?", (internal_number, password))
                if cursor.fetchone():
                    role = "Тренер"
            except ValueError:
                pass 

        # 3. Пользователь (логин: User_ID)
        if not role:
            try:
                user_id = int(username)
                cursor.execute("SELECT User_ID FROM User WHERE User_ID = ? AND Password = ?", (user_id, password))
                if cursor.fetchone():
                    role = "Пользователь"
            except ValueError:
                pass 
                
    except Exception as e:
        print(f"❌ Ошибка БД при аутентификации: {e}")
        
    finally:
        conn.close()
        
    return role


def main_menu(db_name: str, current_user_role: str):
    """
    Динамически строит и обрабатывает меню на основе роли пользователя.
    """
    if current_user_role not in ROLE_POLICY:
        print("Ошибка: Неизвестная роль.")
        return

    allowed_action_keys = ROLE_POLICY[current_user_role]
    
    current_menu_actions = {}
    i = 1
    
    for action_key in allowed_action_keys:
        if action_key in ACTION_MAP:
            # Используем строковое представление i как ключ выбора
            current_menu_actions[str(i)] = ACTION_MAP[action_key]
            i += 1
    
    while True:
        print("\n" + "="*40)
        print(f"       МЕНЮ: {current_user_role.upper()}")
        print("="*40)
        
        for key, (description, _) in current_menu_actions.items():
            # description уже содержит номер, но мы печатаем ключ для выбора
            print(f"{key}. {description.split('. ', 1)[1]}") 
            
        print("0. Выход/Смена пользователя")
        print("="*40)
        
        choice = input("Выберите действие: ")
        
        if choice == '0':
            print(f"\nВыход из системы. До свидания!")
            break
        elif choice in current_menu_actions:
            function_to_call = current_menu_actions[choice][1]
            function_to_call(db_name)
        else:
            print("Некорректный ввод. Пожалуйста, выберите номер из списка.")


def start_program(db_name: str = "coaching.db"):
    """Основная точка входа с циклом аутентификации."""
    while True:
        print("\n" + "="*40)
        print("       СИСТЕМА УПРАВЛЕНИЯ КОУЧИНГОМ")
        print("="*40)
        print("Подсказки для входа:")
        print(" - **Админ**: Логин=admin, Пароль=admin_pass")
        print(" - Тренер (Иванов): Логин=101, Пароль=pass101")
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
            sys.exit() # Использование sys.exit() для завершения программы


# =================================================================
# === 4. ТОЧКА ЗАПУСКА ===
# =================================================================

if __name__ == '__main__':
    DB_NAME = "coaching.db"
    
    try:
        # 1. Инициализация БД
        create_tables(DB_NAME)
        # 2. Вставка тестовых данных (включая Администратора)
        insert_sample_data(DB_NAME)
        
        # 3. Запуск программы
        start_program(DB_NAME)
        
    except Exception as e:
        print(f"Критическая ошибка программы: {e}")