import os
import xml.etree.ElementTree as ET
from typing import Optional 


# 1. УТИЛИТЫ ДЛЯ ВВОДА (Input Validation) ы


def get_validated_input(prompt: str, min_len: int = 1, max_len: int = 50) -> str:
    """
    Запрашивает ввод у пользователя и проверяет его длину.
    """
    while True:
        user_input = input(prompt).strip()
        current_len = len(user_input)

        if current_len == 0 and min_len > 0:
            print("❌ Ввод не может быть пустым. Повторите попытку.")
        elif current_len < min_len:
            print(f"❌ Ввод слишком короткий. Минимальная длина: {min_len} символов.")
        elif current_len > max_len:
            print(f"❌ Ввод слишком длинный ({current_len}). Максимальная длина: {max_len} символов.")
        else:
            return user_input


def get_int_input(prompt: str) -> Optional[int]:
    """Запрашивает числовой ввод с обработкой ошибок."""
    while True:
        value = input(prompt).strip()
        if not value:
            return None # Позволяем пустое значение, если оно не обязательно
        try:
            return int(value)
        except ValueError:
            print("❌ Некорректный ввод. Пожалуйста, введите целое число.")


# 2. УТИЛИТЫ ДЛЯ ЭКСПОРТА

def ensure_output_directory(path: str = "out"):
    """Создает директорию для экспорта, если она еще не существует."""
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"❌ Не удалось создать директорию для экспорта '{path}': {e}")


def indent(elem, level=0):
    """
    Добавляет отступы (пробелы) к XML-элементам для "красивого" вывода (pretty-print).
    """
    if hasattr(ET, 'indent'):
        ET.indent(elem)
        return
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem_child in elem:
            indent(elem_child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i