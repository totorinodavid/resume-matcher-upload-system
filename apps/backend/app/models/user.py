from .base import Base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


class User(Base):
    """
    BULLETPROOF USER MODEL
    - Eindeutige permanente UUID für jeden User
    - Speichert alle Frontend/Backend User Daten
    - Unterstützt Multiple Auth Provider
    """
    __tablename__ = "users"

    # Primary Key - AUTO INCREMENT Integer
    id = Column(Integer, primary_key=True, index=True)
    
    # PERMANENTE USER UUID - Das ist die EINZIGE ID die wir verwenden!
    user_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # User Daten
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    
    # AUTH PROVIDER MAPPING - Speichert alle IDs von verschiedenen Providern
    nextauth_user_id = Column(String, unique=True, nullable=True, index=True)  # NextAuth User ID
    stripe_customer_id = Column(String, unique=True, nullable=True, index=True)  # Stripe Customer ID
    google_user_id = Column(String, unique=True, nullable=True, index=True)  # Google OAuth ID
    github_user_id = Column(String, unique=True, nullable=True, index=True)  # GitHub OAuth ID
    
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
