from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

from app.backend.db import Base
from datetime import date, datetime, timezone


class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    comment = Column(String)
    comment_dt = Column(DateTime(timezone=True), default=datetime.now)
    grade = Column(Integer)
    is_active = Column(Boolean, default=True)
