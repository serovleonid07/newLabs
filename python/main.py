import sys
import os
from typing import Dict, Tuple, Callable, Any, List
from db_config import create_tables, insert_sample_data
from utils import get_validated_input, get_int_input
from repositories.user_repo import UserRepository
from repositories.coach_repo import CoachRepository
from repositories.inventory_repo import InventoryRepository
from repositories.booking_repo import BookingRepository

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 1. ИНИЦИАЛИЗАЦИЯ РЕПОЗИТОРИЕВ

REPOSITORIES: Dict[str, Any] = {}

def initialize_repositories(db_name: str):
    """Инициализирует все репозитории для использования в меню."""
    global REPOSITORIES
    REPOSITORIES = {
        'User': UserRepository(db_name),
        'Coach': CoachRepository(db_name),
        'Inventory': InventoryRepository(db_name),
        'Booking': BookingRepository(db_name),
    }

# 2. ФУНКЦИИ ВВОДА/ВЫВОДА (UI Handlers)

def display_inventory_list() -> List[Dict[str, Any]]:
    """Показывает доступный инвентарь и возвращает его список."""
    inventory = REPOSITORIES['Inventory'].get_all("Inventory")
    if inventory:
        print("\n--- Доступный инвентарь (ID | Название | Кол-во) ---")
        for item in inventory:
            print(f"ID {item['Inventory_ID']}: {item['Name']} (x{item['Count']})")
    else:
        print("ℹ️ Инвентарь отсутствует.")
    return inventory


def add_user_from_console():
    """Интерфейс для добавления нового пользователя."""
    print("\n--- Добавление нового пользователя ---")
    user_data = {
        'Surname': get_validated_input("Введите Фамилию (1-30): ", max_len=30),
        'Name': get_validated_input("Введите Имя (1-30): ", max_len=30),
        'Password': get_validated_input("Введите Пароль (6-30): ", min_len=6, max_len=30)
    }
    if REPOSITORIES['User'].add_user(user_data):
        print("✅ Пользователь успешно добавлен.")
    else:
        print("❌ Не удалось добавить пользователя.")

def add_coach_from_console():
    """Интерфейс для добавления нового тренера."""
    print("\n--- Добавление нового тренера ---")
    coach_data = {
        'Internal_number': get_int_input("Введите Внутренний номер: "),
        'Surname': get_validated_input("Введите Фамилию (1-30): ", max_len=30),
        'Name': get_validated_input("Введите Имя (1-30): ", max_len=30),
        'Experience': get_int_input("Введите Стаж (лет): ") or 0,
        'Password': get_validated_input("Введите Пароль (6-30): ", min_len=6, max_len=30)
    }

    if coach_data['Internal_number'] is None:
        print("❌ Внутренний номер обязателен.")
        return

    if REPOSITORIES['Coach'].add_coach(coach_data):
        print("✅ Тренер успешно добавлен.")
    else:
        print("❌ Не удалось добавить тренера (возможно, номер уже занят).")


def add_booking_from_console():
    """Интерфейс для добавления нового бронирования."""
    print("\n--- Добавление нового бронирования ---")
    
    # 1. Запрос основных данных
    coach_id = get_int_input("Введите ID Тренера: ")
    user_id = get_int_input("Введите ID Пользователя: ")
    time_start = get_validated_input("Введите Время начала (YYYY-MM-DD HH:MM:SS): ", min_len=16)
    time_end = get_validated_input("Введите Время окончания (YYYY-MM-DD HH:MM:SS): ", min_len=16)
    number_booking = get_int_input("Введите Номер бронирования: ")

    if not all([coach_id, user_id, time_start, time_end, number_booking]):
        print("❌ Все поля, кроме инвентаря, обязательны.")
        return

    # 2. Запрос инвентаря
    display_inventory_list()
    inventory_ids_str = input("Введите ID инвентаря через запятую (напр., 1,3,4): ")
    inventory_ids = []
    try:
        if inventory_ids_str.strip():
            inventory_ids = [int(i.strip()) for i in inventory_ids_str.split(',')]
    except ValueError:
        print("❌ Ошибка ввода инвентаря. Используйте только числа, разделенные запятыми.")
        return

    booking_data = {
        'Coach_ID': coach_id, 'User_ID': user_id, 
        'Time_start': time_start, 'Time_end': time_end, 
        'Number_booking': number_booking
    }

    if REPOSITORIES['Booking'].add_booking(booking_data, inventory_ids):
        print("✅ Бронирование и связанный инвентарь успешно добавлены.")
    else:
        print("❌ Не удалось добавить бронирование.")

def add_inventory_from_console():
    """Интерфейс для добавления нового инвентаря."""
    print("\n--- Добавление нового инвентаря ---")
    inventory_data = {
        'Name': get_validated_input("Введите название инвентаря (1-50): ", max_len=50),
        'Count': get_int_input("Введите количество: ")
    }

    if inventory_data['Count'] is None:
        print("❌ Количество обязательно.")
        return

    if REPOSITORIES['Inventory'].add_inventory(inventory_data):
        print("✅ Инвентарь успешно добавлен.")
    else:
        print("❌ Не удалось добавить инвентарь (возможно, название уже существует).")


def modify_data():
    """Общий интерфейс для модификации данных."""
    print("\n--- Модификация данных ---")
    print("[1] Изменить Пользователя")
    print("[2] Изменить Тренера") 
    print("[3] Изменить Инвентарь")
    print("[4] Изменить Бронирование")
    choice = input("Выберите таблицу для изменения: ").strip()
    
    item_id = get_int_input("Введите ID записи для изменения: ")
    if not item_id: return

    if choice == '1':  # User
        user_data = {
            'Surname': get_validated_input("Новая фамилия: ", max_len=30),
            'Name': get_validated_input("Новое имя: ", max_len=30),
            'Password': get_validated_input("Новый пароль: ", min_len=6, max_len=30)
        }
        if REPOSITORIES['User'].update_user(item_id, user_data):
            print("✅ Пользователь обновлен.")
        else:
            print("❌ Ошибка обновления.")
            
    elif choice == '2':  # Coach
        coach_data = {
            'Internal_number': get_int_input("Новый внутренний номер: "),
            'Surname': get_validated_input("Новая фамилия: ", max_len=30),
            'Name': get_validated_input("Новое имя: ", max_len=30),
            'Experience': get_int_input("Новый стаж: ") or 0,
            'Password': get_validated_input("Новый пароль: ", min_len=6, max_len=30)
        }
        if REPOSITORIES['Coach'].update_coach(item_id, coach_data):
            print("✅ Тренер обновлен.")
        else:
            print("❌ Ошибка обновления.")
    elif choice == '3':
        inventory_data = {
            'Name': get_validated_input("Новое название: ", max_len=50),
            'Count': get_int_input("Новое количество: ")
        }
        if REPOSITORIES['Inventory'].update_inventory(item_id, inventory_data):
            print("✅ Инвентарь обновлен.")
        else:
            print("❌ Ошибка обновления инвентаря.")


def delete_data():
    """Общий интерфейс для удаления данных."""
    print("\n--- Удаление данных ---")
    print("[1] Удалить Пользователя")
    print("[2] Удалить Тренера")
    print("[3] Удалить Инвентарь") 
    print("[4] Удалить Бронирование")
    choice = input("Выберите таблицу для удаления: ").strip()
    
    item_id = get_int_input("Введите ID записи для удаления: ")
    if not item_id: return

    if choice == '1':
        if REPOSITORIES['User'].delete_user(item_id):
            print("✅ Пользователь удален.")
    elif choice == '2':
        if REPOSITORIES['Coach'].delete_coach(item_id):
            print("✅ Тренер удален.")
    elif choice == '3':
        if REPOSITORIES['Inventory'].delete_inventory(item_id):
            print("✅ Инвентарь удален.")
    elif choice == '4':
        if REPOSITORIES['Booking'].delete_booking(item_id):
            print("✅ Бронирование удалено.")
    else:
        print("❌ Неверный выбор.")


def display_users():
    """Выводит детали всех пользователей."""
    print("\n--- Список пользователей ---")
    users = REPOSITORIES['User'].display_all_users_details()
    if users:
        for u in users:
            print(f"ID: {u['User_ID']}, {u['Surname']} {u['Name']}, Пароль: {u['Password']}")
    else:
        print("ℹ️ Нет зарегистрированных пользователей.")

def display_coaches():
    """Выводит детали всех тренеров."""
    print("\n--- Список тренеров ---")
    coaches = REPOSITORIES['Coach'].display_all_coaches_details()
    if coaches:
        for c in coaches:
            print(f"ID: {c['Coach_ID']}, Номер: {c['Internal_number']}, {c['Surname']} {c['Name']}, Опыт: {c['Experience']} г., Пароль: {c['Password']}")
    else:
        print("ℹ️ Нет зарегистрированных тренеров.")

def display_bookings_details():
    """Выводит детали всех бронирований."""
    print("\n--- Список бронирований (подробно) ---")
    bookings = REPOSITORIES['Booking'].display_all_bookings_details()
    if bookings:
        for b in bookings:
            inventory = ", ".join(b.pop('Inventory_list')) if b['Inventory_list'] else "Нет инвентаря"
            print(f"ID: {b['Booking_ID']} | Номер: {b['Number_booking']} | Тренер: {b['Coach']} | Пользователь: {b['User']}")
            print(f"    Время: {b['Time_start']} - {b['Time_end']}")
            print(f"    Инвентарь: {inventory}\n")
    else:
        print("ℹ️ Нет активных бронирований.")


def export_flat_data():
    """Интерфейс для плоского экспорта."""
    print("\n--- Универсальный экспорт таблицы ---")
    table_name = get_validated_input("Введите имя таблицы (User, Coach, Inventory): ").capitalize()
    if table_name not in ['User', 'Coach', 'Inventory']: 
        print("❌ Неверное имя таблицы."); return

    file_format = get_validated_input("Выберите формат (json / csv / yaml / xml): ", max_len=4).lower()
    if file_format not in ['json', 'csv', 'yaml', 'xml']:
        print("❌ Неподдерживаемый формат.")
        return

    REPOSITORIES['Booking'].export_table_to_file(table_name, file_format)


def export_nested_booking():
    """Интерфейс для вложенного экспорта бронирований."""
    print("\n--- Вложенный экспорт бронирований ---")
    file_format = get_validated_input("Выберите формат (json / yaml / xml): ", max_len=4).lower()
    if file_format not in ['json', 'yaml', 'xml']:
        print("❌ Неподдерживаемый формат.")
        return
        
    REPOSITORIES['Booking'].export_nested_booking_to_file(file_format)



# 3. МЕНЮ И РОЛИ (Menu & Policy)

# Карта действий (Action Map)
ACTION_MAP: Dict[str, Tuple[str, Callable]] = {
    # CRUD
    "ADD_U": ("Добавить Пользователя", add_user_from_console),
    "ADD_C": ("Добавить Тренера", add_coach_from_console),
    "ADD_B": ("Добавить Бронирование", add_booking_from_console),
    "ADD_I": ("Добавить Инвентарь", add_inventory_from_console),
    "MODIFY": ("Изменить данные", modify_data),
    "DELETE": ("Удалить данные", delete_data),
    # DISPLAY
    "SHOW_U": ("Показать Пользователей", display_users),
    "SHOW_C": ("Показать Тренеров", display_coaches),
    "SHOW_B": ("Показать Бронирования", display_bookings_details),
    # EXPORT
    "EXP_FLAT": ("Экспорт таблицы (JSON/CSV/YAML/XML)", export_flat_data),
    "EXP_NESTED": ("Экспорт Бронирований (вложенный JSON/YAML/XML)", export_nested_booking),
    # EXIT
    "EXIT": ("Выйти из программы", sys.exit)
}

# Политика доступа (Role Policy)
ROLE_POLICY: Dict[str, List[str]] = {
    'Admin': ["ADD_U", "ADD_C", "ADD_B", "ADD_I","MODIFY","DELETE", "SHOW_U", "SHOW_C", "SHOW_B", "EXP_FLAT", "EXP_NESTED", "EXIT"],
    'Coach': ["ADD_U", "ADD_B", "SHOW_C", "SHOW_B", "SHOW_U", "EXIT"],
    'User': ["ADD_B", "SHOW_B", "EXIT"],
}


def main_menu(current_user_role: str):
    """Отображает меню, доступное для текущей роли, и обрабатывает выбор."""
    print(f"\n--- ГЛАВНОЕ МЕНЮ ({current_user_role}) ---")
    available_actions = ROLE_POLICY.get(current_user_role, [])
    
    if not available_actions:
        print("❌ Для вашей роли нет доступных действий.")
        return

    menu_options = {}
    
    # 1. Построение меню
    for i, action_key in enumerate(available_actions, 1):
        description, func = ACTION_MAP[action_key]
        menu_options[str(i)] = {'desc': description, 'func': func, 'key': action_key}
        print(f"[{i}] {description}")
        
    # 2. Выбор действия
    choice = input("\nВыберите действие: ").strip()
    
    selected_option = menu_options.get(choice)
    
    if selected_option:
        try:
            # Вызов функции, соответствующей выбранному действию
            selected_option['func']()
        except Exception as e:
            print(f"\n❌ Произошла ошибка при выполнении действия: {e}")
    else:
        print("❌ Некорректный ввод. Пожалуйста, выберите номер из списка.")

# 4. ТОЧКА ЗАПУСКА

def start_program(db_name: str = "coaching.db"):
    # 1. Инициализация БД и данных
    create_tables(db_name)
    insert_sample_data(db_name)
    initialize_repositories(db_name)

    while True:
        print("\n" + "="*40)
        print(" 🏋️ СИСТЕМА УПРАВЛЕНИЯ КОУЧИНГОМ")
        print("="*40)
        print("Подсказки для входа:")
        print(" - Админ: Логин=1, Пароль=admin_pass")
        print(" - Тренер (Иванов): Логин=102, Пароль=pass102")
        print(" - Пользователь (Климов): Логин=1, Пароль=userpass1")
        
        username = input("Введите Логин: ")
        password = input("Введите Пароль: ")
        
        # Аутентификация через репозиторий
        current_user_role = REPOSITORIES['User'].authenticate(username, password)
        
        if current_user_role:
            print(f"✅ Успешный вход! Ваша роль: **{current_user_role}**.")
            
            # Цикл меню, пока пользователь не выберет выход из программы
            while True:
                try:
                    main_menu(current_user_role)
                except SystemExit:
                    print("\nЗавершение программы.")
                    sys.exit() 
                except Exception as e:
                    print(f"Неизвестная ошибка в меню: {e}")
        else:
            print("❌ Ошибка аутентификации. Неверный логин или пароль.")
        
        continue_choice = input("Хотите попробовать войти снова? (д/н): ").lower()
        if continue_choice != 'д':
            print("\nЗавершение программы.")
            sys.exit() 


if __name__ == '__main__':
    start_program()