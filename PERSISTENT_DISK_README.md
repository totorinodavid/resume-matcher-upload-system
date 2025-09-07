# Persistent Disk & Manual Export

This application supports file uploads with persistent storage and manual export capabilities.

## File Storage

Files are stored on a Render Persistent Disk mounted at `/var/data` (configurable via `FILES_DIR` environment variable). 

### Upload API

Upload files via `POST /api/uploads` with multipart/form-data:

```bash
curl -X POST \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf" \
  -F "userId=user123" \
  -F "kind=resume" \
  http://localhost:3000/api/uploads
```

**Supported file types:**
- PDF (`application/pdf`)
- Word Documents (`.docx`)

**Optional parameters:**
- `userId`: Associate upload with a user
- `kind`: File category (`resume`, `job_posting`, `optimized`, `other`)

### Download Files

Download files via `GET /api/files/{uploadId}`:

```bash
curl http://localhost:3000/api/files/{uploadId} -o downloaded-file.pdf
```

## Admin Operations

Admin operations require authentication via `Authorization: Bearer {ADMIN_TOKEN}` header.

### Check Disk Usage

```bash
curl -H "Authorization: Bearer your-admin-token" \
  http://localhost:3000/api/admin/disk
```

Returns:
```json
{
  "usedPercent": 45,
  "totalBytes": 10737418240,
  "usedBytes": 4831838208,
  "baseDir": "/var/data"
}
```

### Trigger Manual Export

```bash
curl -X POST \
  -H "Authorization: Bearer your-admin-token" \
  http://localhost:3000/api/admin/export
```

This logs an export request. The actual export implementation will be added in future updates.

## Configuration

Required environment variables:

```bash
FILES_DIR=/var/data              # Directory for file storage
ADMIN_TOKEN=change-me           # Admin authentication token
MAX_UPLOAD_MB=20                # Maximum upload size in MB
DATABASE_URL=postgresql://...   # Database connection string
```

## Health Check

The application provides a health endpoint for monitoring:

```bash
curl http://localhost:3000/api/health
```

Returns database connection status and overall health.
