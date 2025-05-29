from collections.abc import Iterable
from abc import ABCMeta
import re
import unicodedata

class Singleton(ABCMeta):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = object.__new__(cls, *args, **kwargs)
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]

# Equivalent to any(), without short-circuiting
def any_nsc(it: Iterable) -> bool:
    result = False
    for a in it:
        result |= bool(a)
    return result

def fix_unicode(s):
    return ''.join(char for char in s if unicodedata.category(char)[0] != 'C')

def unescape(s, encoding='utf-8'):
    s = fix_unicode(s)  # 清理无效字符
    return bytearray(s, encoding=encoding).decode('unicode-escape').encode('utf-8', errors='ignore').decode(encoding)

def full_unescape(s: str) -> str:
    while '\\' in s:
        try:
            s = unescape(s)
        except UnicodeDecodeError:
            return s
    return s