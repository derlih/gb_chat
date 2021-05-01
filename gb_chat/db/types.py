from typing import Type

from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

Base: Type[DeclarativeMeta] = declarative_base()
