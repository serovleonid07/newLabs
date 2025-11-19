# repositories/booking_repo.py
from .base_repo import BaseRepository
from db_config import get_connection # Импортируем для ручного управления транзакциями
from utils import ensure_output_directory, indent
from typing import Dict, Any, List, Optional
import sqlite3
import json
import csv
import yaml
import xml.etree.ElementTree as ET
import os

class BookingRepository(BaseRepository):

    # =================================================================
    # === CRUD: ДОБАВЛЕНИЕ (TRANSACTIONAL) ===
    # =================================================================

    def add_booking(self, booking_data: Dict[str, Any], inventory_ids: List[int]) -> bool:
        """
        Добавляет бронирование и связывает его с инвентарем в рамках одной транзакции.
        """
        conn = None
        try:
            # Ручное управление соединением для транзакции
            conn = get_connection(self._db_name)
            cursor = conn.cursor()

            # 1. Добавление бронирования
            sql_booking = """
                INSERT INTO Booking (Coach_ID, User_ID, Time_start, Time_end, Number_booking) 
                VALUES (?, ?, ?, ?, ?)
            """
            params_booking = (
                booking_data['Coach_ID'], booking_data['User_ID'], 
                booking_data['Time_start'], booking_data['Time_end'], 
                booking_data['Number_booking']
            )
            cursor.execute(sql_booking, params_booking)
            new_booking_id = cursor.lastrowid

            # 2. Добавление инвентаря к бронированию (Статус "Забронировано" = ID 1)
            # Внимание: здесь предполагается, что Status.Status_ID=1 соответствует "Забронировано"
            sql_inventory = "INSERT INTO Booking_inventory (Booking_ID, Inventory_ID, Status_ID) VALUES (?, ?, 1)"
            
            for inventory_id in inventory_ids:
                cursor.execute(sql_inventory, (new_booking_id, inventory_id))

            conn.commit()
            return True
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Ошибка БД при добавлении бронирования. Транзакция отменена: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def update_booking(self, booking_id: int, booking_data: Dict[str, Any]) -> bool:
        """Обновляет данные бронирования."""
        sql = """
            UPDATE Booking SET Coach_ID = ?, User_ID = ?, Time_start = ?, 
            Time_end = ?, Number_booking = ? WHERE Booking_ID = ?
        """
        params = (
            booking_data['Coach_ID'], booking_data['User_ID'],
            booking_data['Time_start'], booking_data['Time_end'],
            booking_data['Number_booking'], booking_id
        )
        return self._execute_non_query(sql, params)

    def delete_booking(self, booking_id: int) -> bool:
        """Удаляет бронирование по ID."""
        sql = "DELETE FROM Booking WHERE Booking_ID = ?"
        return self._execute_non_query(sql, (booking_id,))

    def get_booking_by_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """Получает бронирование по ID."""
        return self.get_by_id("Booking", "Booking_ID", booking_id)

    # =================================================================
    # === READ: ВЫВОД ДЕТАЛЕЙ ===
    # =================================================================

    def display_all_bookings_details(self) -> List[Dict[str, Any]]:
        """Возвращает все бронирования с деталями тренера, пользователя и инвентаря."""
        sql = """
            SELECT 
                B.Booking_ID, B.Time_start, B.Time_end, B.Number_booking,
                C.Surname AS Coach_Surname, C.Name AS Coach_Name, C.Internal_number,
                U.Surname AS User_Surname, U.Name AS User_Name,
                I.Name AS Inventory_Name, S.Name AS Status_Name
            FROM Booking B
            JOIN Coach C ON B.Coach_ID = C.Coach_ID
            JOIN User U ON B.User_ID = U.User_ID
            LEFT JOIN Booking_inventory BI ON B.Booking_ID = BI.Booking_ID
            LEFT JOIN Inventory I ON BI.Inventory_ID = I.Inventory_ID
            LEFT JOIN Status S ON BI.Status_ID = S.Status_ID
            ORDER BY B.Booking_ID
        """
        rows = self._execute_query(sql)
        
        # Группировка данных (если одно бронирование имеет несколько инвентарей)
        grouped_bookings = {}
        for row in rows:
            booking_id = row['Booking_ID']
            if booking_id not in grouped_bookings:
                # Инициализация новой записи о бронировании
                grouped_bookings[booking_id] = {
                    'Booking_ID': row['Booking_ID'],
                    'Number_booking': row['Number_booking'],
                    'Time_start': row['Time_start'],
                    'Time_end': row['Time_end'],
                    'Coach': f"{row['Coach_Surname']} {row['Coach_Name']} ({row['Internal_number']})",
                    'User': f"{row['User_Surname']} {row['User_Name']}",
                    'Inventory_list': []
                }
            
            # Добавление инвентаря к списку, если он существует
            if row['Inventory_Name']:
                grouped_bookings[booking_id]['Inventory_list'].append(
                    f"{row['Inventory_Name']} (Статус: {row['Status_Name']})"
                )

        return list(grouped_bookings.values())


    # =================================================================
    # === ЭКСПОРТ (FLAT Export) ===
    # =================================================================

    def export_table_to_file(self, table_name: str, file_format: str):
        """Универсальный экспорт одной таблицы в JSON, CSV, YAML или XML."""
        
        output_filename = f"{table_name.lower()}.{file_format}"
        output_path = os.path.join("out", output_filename)
        ensure_output_directory()

        # Используем метод базового репозитория
        records = self.get_all(table_name) 
        if not records:
            print(f"ℹ️ Таблица '{table_name}' пуста.")
            return

        try:
            if file_format == 'json':
                self._export_to_json(records, output_path)
            elif file_format == 'csv':
                self._export_to_csv(records, output_path, table_name)
            elif file_format == 'yaml':
                self._export_to_yaml(records, output_path)
            elif file_format == 'xml':
                self._export_to_xml(records, output_path, table_name)
            
            print(f"✅ Данные экспортированы в: {output_path}")
            
        except Exception as e:
            print(f"❌ Ошибка при экспорте в {file_format}: {e}")

    def _export_to_json(self, records: List[Dict], file_path: str):
        """Экспорт в JSON формат."""
        import json
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def _export_to_csv(self, records: List[Dict], file_path: str, table_name: str):
        """Экспорт в CSV формат."""
        import csv
        if not records:
            return
            
        fieldnames = records[0].keys()
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    def _export_to_yaml(self, records: List[Dict], file_path: str):
        """Экспорт в YAML формат."""
        import yaml
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(records, f, allow_unicode=True, default_flow_style=False)

    def _export_to_xml(self, records: List[Dict], file_path: str, table_name: str):
        """Экспорт в XML формат."""
        root = ET.Element(f"{table_name}List")
        
        for record in records:
            item_elem = ET.SubElement(root, table_name[:-1] if table_name.endswith('s') else table_name)
            for key, value in record.items():
                field_elem = ET.SubElement(item_elem, str(key))
                field_elem.text = str(value) if value is not None else ""
        
        indent(root)
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)

    def export_nested_booking_to_file(self, file_format: str):
        """Экспорт бронирований с вложенной структурой (инвентарь внутри брони)."""
        output_filename = f"bookings_nested.{file_format}"
        output_path = os.path.join("out", output_filename)
        ensure_output_directory()

        # Получаем детали бронирований (уже сгруппированные)
        bookings = self.display_all_bookings_details()
        if not bookings:
            print("ℹ️ Нет данных для экспорта.")
            return

        try:
            if file_format == 'json':
                self._export_nested_to_json(bookings, output_path)
            elif file_format == 'yaml':
                self._export_nested_to_yaml(bookings, output_path)
            elif file_format == 'xml':
                self._export_nested_to_xml(bookings, output_path)
            
            print(f"✅ Вложенные данные бронирований экспортированы в: {output_path}")
            
        except Exception as e:
            print(f"❌ Ошибка при вложенном экспорте в {file_format}: {e}")

    def _export_nested_to_json(self, bookings: List[Dict], file_path: str):
        """Экспорт вложенных данных в JSON."""
        import json
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(bookings, f, ensure_ascii=False, indent=2)

    def _export_nested_to_yaml(self, bookings: List[Dict], file_path: str):
        """Экспорт вложенных данных в YAML."""
        import yaml
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(bookings, f, allow_unicode=True, default_flow_style=False)

    def _export_nested_to_xml(self, bookings: List[Dict], file_path: str):
        """Экспорт вложенных данных в XML."""
        root = ET.Element("Bookings")
        
        for booking in bookings:
            booking_elem = ET.SubElement(root, "Booking")
            
            for key, value in booking.items():
                if key == 'Inventory_list':
                    # Обрабатываем список инвентаря отдельно
                    inventory_elem = ET.SubElement(booking_elem, "InventoryList")
                    for item in value:
                        item_elem = ET.SubElement(inventory_elem, "Item")
                        item_elem.text = item
                else:
                    field_elem = ET.SubElement(booking_elem, key)
                    field_elem.text = str(value) if value is not None else ""
        
        indent(root)
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)