from .base import Base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.sql import func


class User(Base):
    """
    USER MODEL - Compatible mit aktueller Datenbank
    EMERGENCY: Verwendet nur existierende Spalten!
    """
    __tablename__ = "users"

    # Primary Key - AUTO INCREMENT Integer
    id = Column(Integer, primary_key=True, index=True)
    
    # User Daten (EXISTIERENDE Spalten)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
    
    # LEGACY IDs - Für Migration/Kompatibilität
    legacy_user_ids = Column(Text, nullable=True)  # JSON Array of old IDs
    
    # STATUS UND METADATA
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # TIMESTAMPS
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(uuid={self.user_uuid}, email={self.email})>"
