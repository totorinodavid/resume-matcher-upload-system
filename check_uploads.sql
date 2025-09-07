-- SQL-Abfrage um alle Uploads zu sehen
SELECT 
  id,
  user_id,
  kind,
  original_filename,
  storage_key,
  mime_type,
  size_bytes,
  created_at
FROM uploads 
ORDER BY created_at DESC 
LIMIT 10;
