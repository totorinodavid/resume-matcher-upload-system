# 🚨 SOFORTIGE LÖSUNG - MANUAL RENDER FIX

## Problem
- Backend seit 20+ Minuten down (404 Fehler)  
- Migration schlägt fehl bei Deployment
- Automatische Fixes funktionieren nicht

## SOFORTIGE AKTION ERFORDERLICH

### Schritt 1: Render Dashboard öffnen
1. Gehe zu: https://dashboard.render.com/web/srv-ctcq6m08fa8c73dv01ng
2. Klicke auf **"Settings"** tab
3. Scroll zu **"Build & Deploy"** 

### Schritt 2: Build Command ändern  
**AKTUELL**: Wahrscheinlich läuft Migration die fehlschlägt
**ÄNDERN ZU**: 
```bash
echo "Skipping migrations for emergency deployment"
```

### Schritt 3: Start Command ändern
**ÄNDERN ZU**:
```bash
uvicorn apps.backend.app.main:app --host 0.0.0.0 --port $PORT
```

### Schritt 4: Environment Variables checken
Stelle sicher dass da ist:
- `DATABASE_URL` (PostgreSQL connection)
- `PYTHON_VERSION` = 3.11

### Schritt 5: Manual Deploy
1. Klicke **"Manual Deploy"**
2. Wähle **"Clear build cache & deploy"**
3. Warte auf Deployment

## Alternative: Rollback auf letzte funktionierende Version
1. Gehe zu **"Deploys"** tab
2. Finde letzte erfolgreiche Deployment  
3. Klicke **"Redeploy"**

## Nach dem Fix:
- Test: https://resume-matcher-backend-j06k.onrender.com/health
- Sollte `{"status": "healthy"}` zurückgeben

## Wenn das nicht funktioniert:
1. Checke **"Logs"** tab in Render
2. Schaue nach Fehlermeldungen
3. Poste hier die Logs für weitere Diagnose

---
**Status**: 🔴 KRITISCH - Manuelle Intervention erforderlich
**Zeit**: Sofort handeln - System ist seit 20+ Minuten down
