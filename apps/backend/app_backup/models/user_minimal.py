from .base import Base
from sqlalchemy import Column, String, Integer


class User(Base):
    """
    ULTRA MINIMAL USER MODEL 
    EMERGENCY: NUR die absolut nötigsten Spalten!
    Keine created_at, updated_at, legacy_user_ids, is_active, etc.
    """
    __tablename__ = "users"

    # Primary Key - AUTO INCREMENT Integer
    id = Column(Integer, primary_key=True, index=True)
    
    # MINIMAL User Daten - NUR was WIRKLICH existiert
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
