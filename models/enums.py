# models/enums.py

from enum import Enum


class Stage(str, Enum):
    FETCH = "FETCH"
    PARSE = "PARSE"
    CHUNK = "CHUNK"
    EMBED = "EMBED"
    STORE = "STORE"
