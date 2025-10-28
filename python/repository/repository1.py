import sqlite3

from python.models.models import Booking, Coach
# Импортируем адаптированные модели


class Repository:
    """
    Класс для взаимодействия с базой данных коучинговой системы (coaching.db).
    Включает методы чтения (Read) и модификации (Create, Update, Delete).
    """
    def __init__(self, db_file: str = "coaching.db"):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row  
        self.cursor = self.conn.cursor()

# --- МЕТОДЫ ЧТЕНИЯ (READ) ---
    
    def get_all_bookings(self) -> list[Booking]:
        """Получает список всех бронирований."""
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
        """Получает информацию о тренере по его ID."""
        query = """
            SELECT Coach_ID, Internal_number, Surname, Name, Experience, Password
            FROM Coach 
            WHERE Coach_ID = ?
        """
        self.cursor.execute(query, (coach_id,))
        row = self.cursor.fetchone()
        if row:
            # Извлекаем Password, чтобы корректно инициализировать модель Coach
            return Coach(
                coach_id=row["Coach_ID"],
                internal_number=row["Internal_number"],
                surname=row["Surname"],
                name=row["Name"],
                experience=row["Experience"],
                password=row["Password"] 
            )
        return None

    def coaches_with_more_than_n_bookings(self, n: int) -> list[Coach]:
        """Находит тренеров, которые имеют более 'n' бронирований."""
        query = """
            SELECT T1.Coach_ID, T1.Internal_number, T1.Surname, T1.Name, T1.Experience, T1.Password
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
                password=row["Password"] # Извлекаем пароль
            ))
        return results

# --- МЕТОДЫ МОДИФИКАЦИИ (CREATE, UPDATE, DELETE) ---

    def add_booking(self, booking: Booking) -> int:
        """
        Добавляет новое бронирование в таблицу Booking. 
        Возвращает ID вставленной записи.
        """
        query = """
            INSERT INTO Booking (Coach_ID, User_ID, Time_start, Time_end, Number_booking) 
            VALUES (?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (
            booking.coach_id, 
            booking.user_id, 
            booking.time_start, 
            booking.time_end, 
            booking.number_booking
        ))
        self.conn.commit()
        return self.cursor.lastrowid
        
    def add_coach(self, coach: Coach) -> int:
        """
        Добавляет нового тренера в таблицу Coach. 
        Возвращает ID вставленной записи.
        """
        query = """
            INSERT INTO Coach (Internal_number, Surname, Name, Experience, Password) 
            VALUES (?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (
            coach.internal_number,
            coach.surname,
            coach.name,
            coach.experience,
            coach.password
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_coach_experience(self, coach_id: int, new_experience: int) -> bool:
        """
        Обновляет поле Experience для тренера.
        Возвращает True, если запись была обновлена.
        """
        query = """
            UPDATE Coach 
            SET Experience = ? 
            WHERE Coach_ID = ?
        """
        self.cursor.execute(query, (new_experience, coach_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_booking(self, booking_id: int) -> bool:
        """
        Удаляет бронирование по его ID.
        Возвращает True, если запись была удалена.
        """
        query = "DELETE FROM Booking WHERE Booking_ID = ?"
        self.cursor.execute(query, (booking_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def close(self):
        """Закрывает соединение с базой данных."""
        self.conn.close()