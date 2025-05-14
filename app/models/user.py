from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLAlchemyEnum
from enum import Enum


class UserRole(str, Enum):
    IS_ADMIN = 'is_admin'
    IS_SUPPLIER = 'is_supplier'
    IS_CUSTOMER = 'is_customer'

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    user_role = Column(SQLAlchemyEnum(UserRole, name='user_role', values_callable=lambda e: [field.value for field in e]),
                       default=UserRole.IS_CUSTOMER)
    is_active = Column(Boolean, default=True)
