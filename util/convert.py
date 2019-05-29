from base64 import b64decode, b64encode
from typing import List


def list_to_b64(l: List[str], separator: str = ',') -> str:
    joined = separator.join(l)
    return b64encode(joined.encode()).decode()


def b64_to_list(b64: str, separator: str = ',') -> List[str]:
    return b64decode(b64).decode().split(separator)
