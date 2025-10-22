# taew/adapters/python/datetime/for_obtaining_current_datetime/__init__.py
from datetime import datetime

now = datetime.now

__all__ = ["now"]
