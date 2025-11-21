# repositories/inventory_repo.py
from .base_repo import BaseRepository
from typing import Dict, Any, Optional

class InventoryRepository(BaseRepository):
    
    def add_inventory(self, inventory_data: Dict[str, Any]) -> bool:
        """Добавляет новый инвентарь."""
        sql = "INSERT INTO Inventory (Name, Count) VALUES (?, ?)"
        params = (inventory_data['Name'], inventory_data['Count'])
        return self._execute_non_query(sql, params)

    def add_status(self, status_data: Dict[str, Any]) -> bool:
        """Добавляет новый статус."""
        sql = "INSERT INTO Status (Name) VALUES (?)"
        params = (status_data['Name'],)
        return self._execute_non_query(sql, params)

    def get_all_statuses(self):
        """Возвращает все статусы."""
        return self.get_all("Status")
    
    def update_inventory(self, inventory_id: int, inventory_data: Dict[str, Any]) -> bool:
        """Обновляет данные инвентаря."""
        sql = "UPDATE Inventory SET Name = ?, Count = ? WHERE Inventory_ID = ?"
        params = (inventory_data['Name'], inventory_data['Count'], inventory_id)
        return self._execute_non_query(sql, params)

    def delete_inventory(self, inventory_id: int) -> bool:
        """Удаляет инвентарь по ID."""
        sql = "DELETE FROM Inventory WHERE Inventory_ID = ?"
        return self._execute_non_query(sql, (inventory_id,))

    def get_inventory_by_id(self, inventory_id: int) -> Optional[Dict[str, Any]]:
        """Получает инвентарь по ID."""
        return self.get_by_id("Inventory", "Inventory_ID", inventory_id)

    def update_status(self, status_id: int, status_data: Dict[str, Any]) -> bool:
        """Обновляет статус."""
        sql = "UPDATE Status SET Name = ? WHERE Status_ID = ?"
        params = (status_data['Name'], status_id)
        return self._execute_non_query(sql, params)

    def delete_status(self, status_id: int) -> bool:
        """Удаляет статус по ID."""
        sql = "DELETE FROM Status WHERE Status_ID = ?"
        return self._execute_non_query(sql, (status_id,))