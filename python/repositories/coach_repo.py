# repositories/coach_repo.py
from .base_repo import BaseRepository
from typing import List, Dict, Any, List, Optional

class CoachRepository(BaseRepository):
    
    def add_coach(self, coach_data: Dict[str, Any]) -> bool:
        """Добавляет нового тренера."""
        sql = """
            INSERT INTO Coach (Internal_number, Surname, Name, Experience, Password) 
            VALUES (?, ?, ?, ?, ?)
        """
        params = (coach_data['Internal_number'], coach_data['Surname'], coach_data['Name'], coach_data['Experience'], coach_data['Password'])
        return self._execute_non_query(sql, params)

    def get_coach_by_internal_number(self, num: int) -> List[Dict[str, Any]]:
        """Получает тренера по внутреннему номеру."""
        sql = "SELECT * FROM Coach WHERE Internal_number = ?"
        rows = self._execute_query(sql, (num,))
        return [dict(row) for row in rows]
    
    def display_all_coaches_details(self) -> List[Dict[str, Any]]:
        """Возвращает все детали тренеров, маскируя пароль."""
        coaches = self.get_all("Coach")
        for coach in coaches:
            coach['Password'] = '*' * len(coach['Password'])
        return coaches
    
    def update_coach(self, coach_id: int, coach_data: Dict[str, Any]) -> bool:
        """Обновляет данные тренера."""
        sql = """
            UPDATE Coach SET Internal_number = ?, Surname = ?, Name = ?, 
            Experience = ?, Password = ? WHERE Coach_ID = ?
        """
        params = (
            coach_data['Internal_number'], coach_data['Surname'], 
            coach_data['Name'], coach_data['Experience'], 
            coach_data['Password'], coach_id
        )
        return self._execute_non_query(sql, params)

    def delete_coach(self, coach_id: int) -> bool:
        """Удаляет тренера по ID."""
        sql = "DELETE FROM Coach WHERE Coach_ID = ?"
        return self._execute_non_query(sql, (coach_id,))

    def get_coach_by_id(self, coach_id: int) -> Optional[Dict[str, Any]]:
        """Получает тренера по ID."""
        return self.get_by_id("Coach", "Coach_ID", coach_id)