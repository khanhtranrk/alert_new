import json
import sqlite3
from datetime import datetime
from schemas import SettingOut

class SettingRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_setting(self, name: str) -> SettingOut:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT name, value FROM settings WHERE name = ?', (name,))
        row = c.fetchone()
        conn.close()

        return SettingOut(name=row[0], value=row[1])

    def update_script(self, name: str, value: str)-> SettingOut:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            UPDATE settings
                SET value = ?
                WHERE name = ?
        ''', (value, name))
        conn.commit()
        conn.close()

        return SettingOut(name=name, value=value)
