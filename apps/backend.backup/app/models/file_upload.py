"""
File Upload Model - Metadaten für hochgeladene Dateien
Ersetzt große Binärdaten in der DB durch Referenzen auf Cloud Storage
"""
from __future__ import annotations

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID

from .base import Base


class FileUpload(Base):
    """
    Metadaten für hochgeladene Dateien
    
    Anstatt große PDFs/DOCX in der DB zu speichern, 
    speichern wir nur Metadaten und Storage-URLs.
    """
    __tablename__ = "file_uploads"
    
    # Primärschlüssel
    id: Mapped[str] = mapped_column(String, primary_key=True)
    
    # User-Zuordnung
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    # Datei-Metadaten
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    storage_url: Mapped[str] = mapped_column(Text, nullable=False)  # URL zu Cloud Storage
    storage_key: Mapped[str] = mapped_column(String, nullable=True)  # Storage-Key/Path
    
    # Datei-Eigenschaften
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=True)  # Bytes
    file_hash: Mapped[str] = mapped_column(String, nullable=True, index=True)  # SHA-256 für Deduplizierung
    
    # Verarbeitungsstatus
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resume_id: Mapped[str] = mapped_column(String, nullable=True)  # FK zu Resume nach Verarbeitung
    
    # Zeitstempel
    created_at: Mapped[str] = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        index=True,
    )
    processed_at: Mapped[str] = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    def __repr__(self) -> str:
        return (
            f"<FileUpload(id={self.id}, "
            f"filename={self.original_filename}, "
            f"processed={self.processed})>"
        )
    
    def as_dict(self) -> dict:
        """Konvertiert zu Dictionary für API-Responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "original_filename": self.original_filename,
            "storage_url": self.storage_url,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "processed": self.processed,
            "resume_id": self.resume_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }
