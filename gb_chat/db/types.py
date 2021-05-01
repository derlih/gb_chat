from typing import Callable, Type

from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm.session import Session

Base: Type[DeclarativeMeta] = declarative_base()
SessionFactory = Callable[[], Session]
