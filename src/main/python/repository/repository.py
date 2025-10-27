import sqlite3
from sqlite3 import Connection
# Импортируем адаптированные модели (предполагая, что они находятся в src.models.models или models.py)
# В реальном коде вам нужно убедиться, что путь импорта верен.
from models.models import Coach, User, Booking # Используем dataclass-модели из предыдущего ответа


class Repository:
    """
    Класс для взаимодействия с базой данных коучинговой системы (coaching.db).
    Адаптирован из репозитория библиотеки.
    """
    def __init__(self, db_file: str = "coaching.db"):
        # Изменяем имя файла базы данных
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row  # Позволяет обращаться к колонкам по имени
        self.cursor = self.conn.cursor()

    def get_all_bookings(self) -> list[Booking]:
        """
        Получает список всех бронирований из таблицы Booking (аналог get_all_books).
        """
        query = """
            SELECT Booking_ID, Coach_ID, User_ID, Time_start, Time_end, Number_booking 
            FROM Booking
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [Booking(
            booking_id=row["Booking_ID"], 
            coach_id=row["Coach_ID"], 
            user_id=row["User_ID"],
            time_start=row["Time_start"],
            time_end=row["Time_end"],
            number_booking=row["Number_booking"]
        ) for row in rows]

    def get_coach(self, coach_id: int) -> Coach | None:
        """
        Получает информацию о тренере по его ID (аналог get_author).
        Пароль не извлекается для безопасности, хотя поле в БД есть.
        """
        query = """
            SELECT Coach_ID, Internal_number, Surname, Name, Experience 
            FROM Coach 
            WHERE Coach_ID = ?
        """
        self.cursor.execute(query, (coach_id,))
        row = self.cursor.fetchone()
        if row:
            # Для модели Coach требуется 6 полей, включая пароль.
            # Мы можем использовать заглушку для пароля при извлечении.
            return Coach(
                coach_id=row["Coach_ID"],
                internal_number=row["Internal_number"],
                surname=row["Surname"],
                name=row["Name"],
                experience=row["Experience"],
                password="" # Заглушка, если поле не извлекается из БД
            )
        return None

    def coaches_with_more_than_n_bookings(self, n: int) -> list[Coach]:
        """
        Находит тренеров, которые имеют более 'n' бронирований (аналог authors_with_more_than_n_books).
        """
        query = """
            SELECT T1.Coach_ID, T1.Internal_number, T1.Surname, T1.Name, T1.Experience
            FROM Coach T1
            JOIN Booking T2 ON T1.Coach_ID = T2.Coach_ID
            GROUP BY T1.Coach_ID
            HAVING COUNT(T2.Booking_ID) > ?
        """
        self.cursor.execute(query, (n,))
        rows = self.cursor.fetchall()
        
        results = []
        for row in rows:
            results.append(Coach(
                coach_id=row["Coach_ID"],
                internal_number=row["Internal_number"],
                surname=row["Surname"],
                name=row["Name"],
                experience=row["Experience"],
                password="" # Заглушка
            ))
        return results

    def close(self):
        """Закрывает соединение с базой данных."""
        self.conn.close()