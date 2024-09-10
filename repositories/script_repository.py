import json
import sqlite3
from datetime import datetime
from typing import List
from schemas import Script, ScriptOut

class ScriptRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_scripts(self) -> List[ScriptOut]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, name, begin, config, phrases, phrases_bytes FROM scripts')
        rows = c.fetchall()
        conn.close()

        return [ScriptOut(id=sid, name=name, begin=datetime.fromisoformat(begin), config=json.loads(config), phrases=json.loads(phrases), phrases_bytes=phrases_bytes) for sid, name, begin, config, phrases, phrases_bytes in rows]

    def get_script(self, sid: int) -> ScriptOut:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, name, begin, config, phrases, phrases_bytes FROM scripts WHERE id = ?', (sid,))
        row = c.fetchone()
        conn.close()
        return ScriptOut(
            id=row[0],
            name=row[1],
            begin=datetime.fromisoformat(row[2]),
            config=json.loads(row[3]),
            phrases=json.loads(row[4]),
            phrases_bytes=row[5]
        )

    def insert_script(self, script: Script) -> ScriptOut:
        config_json = json.dumps(script.config.__dict__)
        phrases_json = json.dumps([phrase.__dict__ for phrase in script.phrases])
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO scripts (name, begin, config, phrases, phrases_bytes)
            VALUES (?, ?, ?, ?, ?)
        ''', (script.name, script.begin.isoformat(), config_json, phrases_json, script.phrases_bytes))
        new_id = c.lastrowid
        conn.commit()
        conn.close()
        return ScriptOut(
            id=new_id,
            name=script.name,
            begin=script.begin,
            config=script.config,
            phrases=script.phrases,
            phrases_bytes=script.phrases_bytes
        )
    
    def update_script(self, sid: int, script: Script)-> ScriptOut:
        config_json = json.dumps(script.config.__dict__)
        phrases_json = json.dumps([phrase.__dict__ for phrase in script.phrases])

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            UPDATE scripts
                SET name = ?, begin = ?, config = ?, phrases = ?, phrases_bytes = ?
                WHERE id = ?
        ''', (script.name, script.begin.isoformat(), config_json, phrases_json, script.phrases_bytes, sid))
        conn.commit()
        conn.close()
        return ScriptOut(
            id=sid,
            name=script.name,
            begin=script.begin,
            config=script.config,
            phrases=script.phrases,
            phrases_bytes=script.phrases_bytes
        )

    def delete_script(self, sid: int):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM scripts WHERE id = ?', (sid,))
        conn.commit()
        conn.close()
