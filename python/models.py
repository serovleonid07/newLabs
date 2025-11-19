from dataclasses import dataclass
from typing import Optional

# =================================================================
# === СТРУКТУРЫ ДАННЫХ (МОДЕЛИ) ===
# =================================================================

@dataclass
class User:
    """Модель Пользователя."""
    user_id: Optional[int]
    surname: str
    name: str
    password: str 


@dataclass
class Coach(User):
    """
    Модель Тренера. Наследует свойства Пользователя.
    """
    internal_number: int
    experience: Optional[int] = 0


@dataclass
class Status:
    """Модель Статуса (для бронирования инвентаря)."""
    status_id: Optional[int]
    name: str


@dataclass
class Inventory:
    """Модель Инвентаря."""
    inventory_id: Optional[int]
    name: str
    count: int # Доступное количество


@dataclass
class Booking:
    """Модель Бронирования."""
    booking_id: Optional[int]
    coach_id: int 
    user_id: int
    time_start: str 
    time_end: str   
    number_booking: int 


@dataclass
class BookingInventoryLink:
    """Модель для таблицы-связки Booking_inventory."""
    booking_id: int
    inventory_id: int
    status_id: int