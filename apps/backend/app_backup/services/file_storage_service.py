"""
File Storage Service - Sichere File-Upload-Behandlung
Ersetzt direkte DB-Storage durch Cloud-Storage mit signed URLs
"""
import os
import uuid
import hashlib
import logging
import tempfile
from typing import Dict, Optional, Tuple, BinaryIO
from pathlib import Path
import mimetypes

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

logger = logging.getLogger(__name__)


class FileStorageService:
    """
    Sicherer File-Storage-Service für Resume-Uploads
    
    Architektur:
    1. Client holt signed upload URL
    2. Client lädt direkt in Cloud Storage hoch
    3. Backend verarbeitet nur Metadaten + Storage-URL
    4. Keine großen Binärdateien in der Datenbank
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.max_file_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        self.allowed_mime_types = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
    
    async def create_signed_upload_url(
        self, 
        filename: str, 
        content_type: str,
        user_id: str
    ) -> Dict[str, str]:
        """
        Erstellt eine sichere signed URL für direkten Client-Upload
        
        Args:
            filename: Original-Dateiname
            content_type: MIME-Type der Datei
            user_id: User-ID für Zuordnung
            
        Returns:
            Dict mit upload_url, file_id und storage_path
            
        Raises:
            ValueError: Bei ungültigen Parametern
        """
        # Validierung
        if not filename or not content_type or not user_id:
            raise ValueError("filename, content_type und user_id sind erforderlich")
        
        if content_type not in self.allowed_mime_types:
            raise ValueError(f"Nicht unterstützter MIME-Type: {content_type}")
        
        # Sichere Dateinamen generieren
        file_id = str(uuid.uuid4())
        safe_filename = self._sanitize_filename(filename)
        extension = self._get_extension_from_mime(content_type)
        
        # Storage-Pfad: user_id/file_id/filename
        storage_key = f"uploads/{user_id}/{file_id}/{safe_filename}{extension}"
        
        # Hier würde normalerweise eine Cloud-Storage-Integration stehen
        # Für jetzt simulieren wir mit lokalem Storage
        if settings.USE_CLOUD_STORAGE:
            upload_url = await self._create_cloud_signed_url(storage_key, content_type)
            storage_url = f"{settings.CLOUD_STORAGE_BASE_URL}/{storage_key}"
        else:
            # Lokales Storage für Development
            upload_url = f"file://local/{storage_key}"
            storage_url = f"{settings.LOCAL_STORAGE_PATH}/{storage_key}"
        
        logger.info(f"Created signed upload URL for user_id={user_id} file_id={file_id}")
        
        return {
            "upload_url": upload_url,
            "file_id": file_id,
            "storage_key": storage_key,
            "storage_url": storage_url,
            "expires_in": 3600  # 1 Stunde
        }
    
    async def process_uploaded_file(
        self,
        file_id: str,
        storage_url: str,
        user_id: str,
        original_filename: str,
        content_type: str
    ) -> Dict[str, str]:
        """
        Verarbeitet eine hochgeladene Datei nach dem Upload
        
        Args:
            file_id: Eindeutige File-ID
            storage_url: URL zur Datei im Storage
            user_id: User-ID
            original_filename: Original-Dateiname
            content_type: MIME-Type
            
        Returns:
            Dict mit processing-Informationen
        """
        try:
            # 1. Datei-Metadaten in DB speichern
            from app.models import FileUpload
            
            # Hash für Deduplizierung (später, wenn Datei verarbeitet wird)
            file_upload = FileUpload(
                id=file_id,
                user_id=user_id,
                original_filename=original_filename,
                storage_url=storage_url,
                mime_type=content_type,
                processed=False
            )
            
            self.db.add(file_upload)
            await self.db.commit()
            
            # 2. Datei zur Verarbeitung weiterleiten
            processing_result = await self._process_file_content(
                file_id=file_id,
                storage_url=storage_url,
                content_type=content_type
            )
            
            logger.info(f"File processed successfully file_id={file_id}")
            
            return {
                "file_id": file_id,
                "status": "processed",
                "resume_id": processing_result.get("resume_id"),
                "storage_url": storage_url
            }
            
        except Exception as e:
            logger.error(f"Failed to process uploaded file file_id={file_id}: {e}")
            await self.db.rollback()
            raise RuntimeError(f"File processing failed: {str(e)}") from e
    
    async def _process_file_content(
        self,
        file_id: str,
        storage_url: str,
        content_type: str
    ) -> Dict[str, str]:
        """
        Lädt Datei aus Storage und verarbeitet sie mit MarkItDown
        
        Args:
            file_id: File-ID
            storage_url: Storage-URL
            content_type: MIME-Type
            
        Returns:
            Processing-Ergebnis mit resume_id
        """
        temp_file_path = None
        
        try:
            # 1. Datei aus Storage laden
            file_content = await self._download_from_storage(storage_url)
            
            # 2. Temporäre Datei erstellen
            extension = self._get_extension_from_mime(content_type)
            with tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=extension
            ) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            # 3. Mit bestehender Resume-Service-Logic verarbeiten
            from app.services import ResumeService
            
            resume_service = ResumeService(self.db)
            resume_id = await resume_service.convert_and_store_resume(
                file_bytes=file_content,
                file_type=content_type,
                filename=f"upload_{file_id}{extension}",
                content_type="md",
                defer_structured=False  # Sofort verarbeiten für bessere UX
            )
            
            # 4. File-Upload als verarbeitet markieren
            await self._mark_file_processed(file_id, resume_id)
            
            return {
                "resume_id": resume_id,
                "processed": True
            }
            
        finally:
            # Temporäre Datei löschen
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    async def _download_from_storage(self, storage_url: str) -> bytes:
        """
        Lädt Datei aus Storage (Cloud oder lokal)
        
        Args:
            storage_url: URL zur Datei
            
        Returns:
            Datei-Content als bytes
        """
        if storage_url.startswith("file://local/"):
            # Lokaler Storage für Development
            local_path = storage_url.replace("file://local/", "")
            full_path = Path(settings.LOCAL_STORAGE_PATH) / local_path
            
            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {full_path}")
            
            return full_path.read_bytes()
        
        elif storage_url.startswith("https://"):
            # Cloud Storage (S3, R2, etc.)
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(storage_url) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Failed to download file: HTTP {response.status}")
                    
                    return await response.read()
        
        else:
            raise ValueError(f"Unsupported storage URL format: {storage_url}")
    
    async def _mark_file_processed(self, file_id: str, resume_id: str):
        """Markiert File-Upload als verarbeitet"""
        from app.models import FileUpload
        from sqlalchemy import select, update
        
        await self.db.execute(
            update(FileUpload)
            .where(FileUpload.id == file_id)
            .values(processed=True, resume_id=resume_id)
        )
        await self.db.commit()
    
    async def _create_cloud_signed_url(self, storage_key: str, content_type: str) -> str:
        """
        Erstellt signed URL für Cloud Storage (S3, Cloudflare R2, etc.)
        
        TODO: Implementation für gewünschten Cloud-Provider
        """
        # Beispiel für AWS S3:
        # import boto3
        # s3_client = boto3.client('s3')
        # return s3_client.generate_presigned_url(
        #     'put_object',
        #     Params={'Bucket': settings.S3_BUCKET, 'Key': storage_key, 'ContentType': content_type},
        #     ExpiresIn=3600
        # )
        
        # Für jetzt Dummy-URL
        return f"https://storage.example.com/signed-upload/{storage_key}?signature=dummy"
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Bereinigt Dateinamen für sichere Storage
        
        Args:
            filename: Original-Dateiname
            
        Returns:
            Bereinigte Version
        """
        # Entferne gefährliche Zeichen
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
        name_without_ext = Path(filename).stem
        
        sanitized = ''.join(c if c in safe_chars else '_' for c in name_without_ext)
        
        # Begrenze Länge
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        
        return sanitized or "upload"
    
    def _get_extension_from_mime(self, content_type: str) -> str:
        """
        Ermittelt Datei-Extension aus MIME-Type
        
        Args:
            content_type: MIME-Type
            
        Returns:
            Datei-Extension mit Punkt (z.B. ".pdf")
        """
        mime_to_ext = {
            "application/pdf": ".pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"
        }
        
        return mime_to_ext.get(content_type, "")
