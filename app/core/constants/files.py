from enum import Enum
from pathlib import Path

from aiogram.types import FSInputFile

STATIC_DIR = Path.cwd() / "static"
GREETING = FSInputFile(str(STATIC_DIR / "greeting.gif"))


class Images(Enum):
    GREETING = FSInputFile(str(STATIC_DIR / "greeting.gif"))
