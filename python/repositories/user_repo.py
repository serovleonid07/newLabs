# repositories/user_repo.py
from .base_repo import BaseRepository
from typing import List, Dict, Any, Optional

class UserRepository(BaseRepository):
    
    def authenticate(self, login: str, password: str) -> Optional[str]:
        """
        Проверяет учетные данные пользователя/тренера и возвращает его роль.
        """
        # 1. Проверяем в таблице Coach (Админ/Тренер)
        sql_coach = "SELECT Coach_ID, Password FROM Coach WHERE Internal_number = ? OR Coach_ID = ?"
        params = (login, login)
        
        # Для admin, login='admin' (str) не совпадает с Internal_number (int), 
        # но совпадает с Coach_ID=1 (если login='1').
        
        # Лучше сделать две явные проверки
        
        # Проверка по Internal_number для тренеров (включая админа с номером 1)
        if login.isdigit():
            sql= "SELECT Coach_ID, Password FROM Coach WHERE Internal_number = ?"
            result = self._execute_query(sql, (int(login),))
        else: # Проверка админа по специальному логину 'admin'
            sql = "SELECT Coach_ID, Password FROM Coach WHERE Name = 'Admin' AND Surname = 'Adminov'" # или другой уникальный признак
            result = self._execute_query(sql)
            
        if result and dict(result[0])['Password'] == password:
                return 'Admin' if dict(result[0])['Coach_ID'] == 1 else 'Coach'

        # 2. Проверяем в таблице User (Пользователь)
        if login.isdigit():
            sql = "SELECT Password FROM User WHERE User_ID = ?"
            result = self._execute_query(sql, (int(login),))
            if result and dict(result[0])['Password'] == password:
                return 'User'

        return None

    def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Добавляет нового пользователя."""
        sql = "INSERT INTO User (Surname, Name, Password) VALUES (?, ?, ?)"
        params = (user_data['Surname'], user_data['Name'], user_data['Password'])
        return self._execute_non_query(sql, params)

    def display_all_users_details(self) -> List[Dict[str, Any]]:
        """Возвращает все детали пользователей, маскируя пароль."""
        users = self.get_all("User")
        for user in users:
            # Маскировка пароля для вывода
            user['Password'] = '*' * len(user['Password'])
        return users
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        """Обновляет данные пользователя."""
        sql = "UPDATE User SET Surname = ?, Name = ?, Password = ? WHERE User_ID = ?"
        params = (user_data['Surname'], user_data['Name'], user_data['Password'], user_id)
        return self._execute_non_query(sql, params)

    def delete_user(self, user_id: int) -> bool:
        """Удаляет пользователя по ID."""
        sql = "DELETE FROM User WHERE User_ID = ?"
        return self._execute_non_query(sql, (user_id,))

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает пользователя по ID."""
        return self.get_by_id("User", "User_ID", user_id)
    # ... Добавить остальные CRUD методы для User
