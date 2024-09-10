from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Config(BaseModel):
    custom_1: int
    custom_2: int
    noise: int

class Phrase(BaseModel):
    tone: int
    tone_noise: int
    echo: int
    echo_noise: int
    delay: int
    loop: int

class Script(BaseModel):
    name: str
    begin: datetime
    config: Config
    phrases: List[Phrase]
    phrases_bytes: Optional[bytes] = None

class ScriptOut(BaseModel):
    id: int
    name: str
    begin: datetime
    config: Config
    phrases: List[Phrase]
    phrases_bytes: Optional[bytes] = None

class SettingOut(BaseModel):
    name: str
    value: str

class Setting(BaseModel):
    name: str
    value: str

