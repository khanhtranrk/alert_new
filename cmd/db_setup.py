import os
import sqlite3

db_name = 'alert.db'
dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
db_path = os.path.join(dir_path, db_name)

def create_scripts_table():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            begin TEXT NOT NULL,
            config TEXT NOT NULL,
            phrases TEXT NOT NULL,
            phrases_bytes BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def create_settings_table():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            name TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_settings_data():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO settings (name, value)
        VALUES ('script', '')
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    if os.path.exists(db_path):
        os.remove(db_path)

    # Create tables
    create_scripts_table()
    create_settings_table()

    # Insert data
    insert_settings_data()
