# models/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Shared declarative base, No relationships defined anywhere off this base - every joi is writtent explicitly at the query site"""
    pass
