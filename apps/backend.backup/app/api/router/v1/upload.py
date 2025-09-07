"""
Sichere File Upload API - Signed URLs statt direkte DB-Storage
"""
import logging
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db_session
from app.core.auth import require_auth, Principal
from app.services.file_storage_service import FileStorageService
from app.core.error_codes import to_error_payload

logger = logging.getLogger(__name__)
upload_router = APIRouter(tags=["upload"])


class CreateUploadUrlRequest(BaseModel):
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the file")


class ProcessUploadRequest(BaseModel):
    file_id: str = Field(..., description="File ID from upload URL creation")
    storage_url: str = Field(..., description="Storage URL where file was uploaded")


@upload_router.post(
    "/create-url",
    summary="Create signed upload URL",
    description="Creates a secure signed URL for direct client-to-storage upload. No file data goes through server."
)
async def create_upload_url(
    request: Request,
    payload: CreateUploadUrlRequest,
    db: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(require_auth),
):
    """
    Erstellt eine sichere signed URL für direkten Client-Upload.
    
    Security Benefits:
    - Keine großen Dateien durch Server
    - Reduzierte Server-Last
    - Bessere Performance
    - Skalierbarkeit
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))
    user_id = principal.user_id
    
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "request_id": request_id,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "User authentication required"
                }
            }
        )
    
    try:
        file_storage_service = FileStorageService(db)
        
        result = await file_storage_service.create_signed_upload_url(
            filename=payload.filename,
            content_type=payload.content_type,
            user_id=user_id
        )
        
        logger.info(f"Upload URL created for user_id={user_id} filename={payload.filename}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "request_id": request_id,
                "data": {
                    "upload_url": result["upload_url"],
                    "file_id": result["file_id"],
                    "storage_key": result["storage_key"],
                    "expires_in": result["expires_in"]
                }
            }
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in upload URL creation: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "request_id": request_id,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e)
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to create upload URL: {e}")
        code, body = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=body)


@upload_router.post(
    "/process",
    summary="Process uploaded file",
    description="Processes a file after it has been uploaded to storage. Extracts content and creates resume."
)
async def process_uploaded_file(
    request: Request,
    payload: ProcessUploadRequest,
    db: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(require_auth),
    defer: bool = Query(False, description="Defer structured extraction (faster response)")
):
    """
    Verarbeitet eine hochgeladene Datei nach dem Upload.
    
    Workflow:
    1. Client ruft /create-url auf
    2. Client lädt direkt in Storage hoch
    3. Client ruft /process auf
    4. Server lädt aus Storage, verarbeitet, speichert Metadaten
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))
    user_id = principal.user_id
    
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "request_id": request_id,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "User authentication required"
                }
            }
        )
    
    try:
        file_storage_service = FileStorageService(db)
        
        # TODO: Hier sollten wir die original filename und content_type aus der DB holen
        # Vorerst Dummy-Werte
        result = await file_storage_service.process_uploaded_file(
            file_id=payload.file_id,
            storage_url=payload.storage_url,
            user_id=user_id,
            original_filename="uploaded_file",  # TODO: Aus DB holen
            content_type="application/pdf"      # TODO: Aus DB holen
        )
        
        logger.info(f"File processed for user_id={user_id} file_id={payload.file_id}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "request_id": request_id,
                "data": {
                    "file_id": result["file_id"],
                    "resume_id": result["resume_id"],
                    "status": result["status"],
                    "processing": "deferred" if defer else "complete"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to process uploaded file: {e}")
        code, body = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=body)


@upload_router.get(
    "/status/{file_id}",
    summary="Get upload processing status",
    description="Returns the current processing status of an uploaded file."
)
async def get_upload_status(
    request: Request,
    file_id: str,
    db: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(require_auth),
):
    """
    Holt den aktuellen Verarbeitungsstatus eines Uploads.
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))
    user_id = principal.user_id
    
    try:
        from app.models import FileUpload
        from sqlalchemy import select
        
        # File-Upload aus DB holen
        result = await db.execute(
            select(FileUpload).where(
                FileUpload.id == file_id,
                FileUpload.user_id == user_id  # Security: Nur eigene Files
            )
        )
        file_upload = result.scalar_one_or_none()
        
        if not file_upload:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "request_id": request_id,
                    "error": {
                        "code": "FILE_NOT_FOUND",
                        "message": f"File with ID {file_id} not found"
                    }
                }
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "request_id": request_id,
                "data": {
                    "file_id": file_upload.id,
                    "filename": file_upload.original_filename,
                    "processed": file_upload.processed,
                    "resume_id": file_upload.resume_id,
                    "created_at": file_upload.created_at.isoformat() if file_upload.created_at else None,
                    "processed_at": file_upload.processed_at.isoformat() if file_upload.processed_at else None
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get upload status: {e}")
        code, body = to_error_payload(e, request_id)
        return JSONResponse(status_code=code, content=body)
