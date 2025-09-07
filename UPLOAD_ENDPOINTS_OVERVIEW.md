# Upload-Verwaltung - Übersicht der Endpunkte

## 📤 Upload-Endpunkte

### 1. Datei hochladen
```bash
POST /api/uploads
Content-Type: multipart/form-data

# Beispiel mit curl:
curl -X POST \
  -F "file=@resume.pdf" \
  -F "userId=user123" \
  -F "kind=resume" \
  http://localhost:3000/api/uploads
```

### 2. Datei herunterladen
```bash
GET /api/files/{uploadId}

# Beispiel:
curl http://localhost:3000/api/files/a1b2c3d4-e5f6-7890-abcd-ef1234567890 -o datei.pdf
```

## 🔧 Admin-Endpunkte (benötigen ADMIN_TOKEN)

### 3. Festplatten-Status prüfen
```bash
GET /api/admin/disk
Authorization: Bearer {ADMIN_TOKEN}

# Beispiel:
curl -H "Authorization: Bearer change-me" \
  http://localhost:3000/api/admin/disk
```

**Antwort:**
```json
{
  "usedPercent": 45,
  "totalBytes": 10737418240,
  "usedBytes": 4831838208,
  "baseDir": "/var/data"
}
```

### 4. Export anfordern
```bash
POST /api/admin/export
Authorization: Bearer {ADMIN_TOKEN}

# Beispiel:
curl -X POST \
  -H "Authorization: Bearer change-me" \
  http://localhost:3000/api/admin/export
```

## 📊 Datenbank-Abfragen

### Alle Uploads anzeigen:
```sql
SELECT 
  id,
  user_id,
  kind,
  original_filename,
  storage_key,
  mime_type,
  size_bytes / 1024 / 1024 as size_mb,
  created_at
FROM uploads 
ORDER BY created_at DESC;
```

### Uploads nach Benutzer:
```sql
SELECT 
  user_id,
  COUNT(*) as upload_count,
  SUM(size_bytes) / 1024 / 1024 as total_mb
FROM uploads 
GROUP BY user_id
ORDER BY upload_count DESC;
```

### Uploads nach Typ:
```sql
SELECT 
  kind,
  COUNT(*) as count,
  AVG(size_bytes) / 1024 / 1024 as avg_size_mb
FROM uploads 
GROUP BY kind
ORDER BY count DESC;
```

## 🏥 System-Gesundheit

### Health Check:
```bash
GET /api/health

# Beispiel:
curl http://localhost:3000/api/health
```

**Antwort:**
```json
{
  "ok": true,
  "database": { "ok": true },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 🔧 Entwicklung & Debugging

### Lokale Entwicklung:
```bash
# Server starten
npm run dev

# Tests ausführen
npm test

# Prisma Studio öffnen (für DB-Visualisierung)
npx prisma studio
```

### Logs überprüfen:
```bash
# Upload-Logs mit strukturierten Daten:
# - uploadId
# - originalFilename  
# - sizeBytes
# - mimeType
# - userId
# - requestId
```

## 📁 Datei-Struktur

```
/var/data/uploads/
├── {hash[0:2]}/     # Erste 2 Zeichen des SHA1-Hash
│   └── {hash[2:4]}/ # Nächste 2 Zeichen des SHA1-Hash  
│       └── {uuid}__{filename}
```

**Beispiel:**
- UUID: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- SHA1: `d85b1213473c2fd7c2045020a6b9c62b6f40c987`
- Pfad: `/var/data/uploads/d8/5b/a1b2c3d4-e5f6-7890-abcd-ef1234567890__resume.pdf`
