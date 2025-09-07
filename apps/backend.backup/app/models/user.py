"""
Production-compatible user model that works with existing schema.
"""

from .base import Base
from sqlalchemy import Column, String, Integer


class User(Base):
    """
    PRODUCTION-COMPATIBLE USER MODEL
    Works with existing production schema and new hotfix schema.
    """
    __tablename__ = "users"

    # Primary Key - AUTO INCREMENT Integer (existing)
    id = Column(Integer, primary_key=True, index=True)
    
    # Existing columns in production
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    
    # New column - will be added by migration
    # Using server_default to handle existing rows
    credits_balance = Column(Integer, nullable=False, default=0, server_default="0")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}', credits={getattr(self, 'credits_balance', 0)})>"
