# repositories/base_repo.py
from db_config import get_connection
import sqlite3
from typing import List, Any, Dict, Optional

class BaseRepository:
    def __init__(self, db_name: str = "coaching.db"):
        self._db_name = db_name

    def _execute_query(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Выполняет SELECT запрос и возвращает результат в виде списка sqlite3.Row."""
        conn = None
        try:
            conn = get_connection(self._db_name)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Ошибка БД при чтении: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def _execute_non_query(self, sql: str, params: tuple = ()) -> bool:
        """Выполняет INSERT, UPDATE, DELETE запросы и возвращает статус успеха."""
        conn = None
        try:
            conn = get_connection(self._db_name)
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка БД при записи: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Возвращает все записи из указанной таблицы."""
        sql = f"SELECT * FROM {table_name}"
        rows = self._execute_query(sql)
        return [dict(row) for row in rows]
    
    def get_by_id(self, table_name: str, id_col: str, item_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает запись по ID."""
        sql = f"SELECT * FROM {table_name} WHERE {id_col} = ?"
        rows = self._execute_query(sql, (item_id,))
        return dict(rows[0]) if rows else None