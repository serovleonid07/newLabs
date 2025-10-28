# models/models.py (Адаптировано)

class Coach:
    """
    Модель для таблицы Coach
    Поля:
    - coach_id: уникальный идентификатор тренера (PK)
    - internal_number: внутренний номер
    - surname: фамилия
    - name: имя
    - experience: опыт работы (в годах, int)
    - password: пароль (хотя в репозитории обычно не используется)
    """
    def __init__(self, coach_id, internal_number, surname, name, experience, password):
        self.coach_id = coach_id
        self.internal_number = internal_number
        self.surname = surname
        self.name = name
        self.experience = experience
        self.password = password

class User:
    """
    Модель для таблицы User
    Поля:
    - user_id: уникальный идентификатор пользователя (PK)
    - surname: фамилия
    - name: имя
    - password: пароль
    """
    def __init__(self, user_id, surname, name, password):
        self.user_id = user_id
        self.surname = surname
        self.name = name
        self.password = password
        
class Booking:
    """
    Модель для таблицы Booking
    Поля:
    - booking_id: уникальный идентификатор бронирования (PK)
    - coach_id: идентификатор тренера (FK -> Coach.Coach_ID)
    - user_id: идентификатор пользователя (FK -> User.User_ID)
    - time_start: время начала бронирования (date/time)
    - time_end: время окончания бронирования (date/time)
    - number_booking: номер бронирования
    """
    def __init__(self, booking_id, coach_id, user_id, time_start, time_end, number_booking):
        self.booking_id = booking_id
        self.coach_id = coach_id
        self.user_id = user_id
        self.time_start = time_start
        self.time_end = time_end
        self.number_booking = number_booking
        
# Примечание: В реальной системе также могут понадобиться модели для Inventory, Status и Booking_inventory.
# Для простоты, как правило, моделируют только основные сущности.