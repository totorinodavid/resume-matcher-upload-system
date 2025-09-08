# Logo-Problem Lösung - Dokumentation

## Problem
Das Logo wurde nicht richtig angezeigt, weil das Backend-Clean-Service kein `public`-Verzeichnis mit den Logo-Dateien hatte.

## Ursache
- Das Frontend (`apps/frontend/public/`) enthielt alle Logo-Dateien
- Das Backend (`apps/backend-clean/public/`) existierte nicht
- Das Dockerfile kopierte das public-Verzeichnis, aber es war leer/nicht vorhanden

## Lösung
1. **Public-Verzeichnis erstellt**: `apps/backend-clean/public/`
2. **Logo-Dateien kopiert** vom Frontend zum Backend:
   - `LOGO.png`
   - `wort_logo.png` 
   - `wort_logo.svg`
   - `logo.svg`
   - `logo-icon.svg`

## Kopierte Dateien
```
Frontend: apps/frontend/public/LOGO.png
Backend:  apps/backend-clean/public/LOGO.png

Frontend: apps/frontend/public/wort_logo.png  
Backend:  apps/backend-clean/public/wort_logo.png

Frontend: apps/frontend/public/wort_logo.svg
Backend:  apps/backend-clean/public/wort_logo.svg

Frontend: apps/frontend/public/logo.svg
Backend:  apps/backend-clean/public/logo.svg

Frontend: apps/frontend/public/logo-icon.svg
Backend:  apps/backend-clean/public/logo-icon.svg
```

## Deployment-Überprüfung
Nach dem Fix sind die Logos unter diesen URLs verfügbar:
- Backend: `http://localhost:3000/LOGO.png`
- Backend: `http://localhost:3000/wort_logo.png`
- Frontend: `http://localhost:3001/LOGO.png`  
- Frontend: `http://localhost:3001/wort_logo.png`

## Docker-Build
Das Dockerfile wurde nicht geändert, da es bereits korrekt konfiguriert war:
```dockerfile
COPY --from=build /app/public ./public
RUN [ -d public ] || mkdir -p public
```

## Für zukünftige Deployments
Stellen Sie sicher, dass:
1. Das `apps/backend-clean/public/`-Verzeichnis existiert
2. Alle Logo-Dateien vom Frontend synchronisiert sind
3. Docker Build läuft ohne Fehler durch

## Getestete URLs (Status: ✅ OK)
- http://localhost:3000 (Backend Homepage)
- http://localhost:3000/LOGO.png (Logo verfügbar)
- http://localhost:3000/wort_logo.png (Logo verfügbar)
- http://localhost:3001 (Frontend mit Logos)

## Fix-Datum
9. September 2025

## Automatisierung
Für zukünftige Sync könnte ein Script erstellt werden:
```bash
# sync-logos.sh
cp apps/frontend/public/LOGO.png apps/backend-clean/public/
cp apps/frontend/public/wort_logo.* apps/backend-clean/public/  
cp apps/frontend/public/logo*.svg apps/backend-clean/public/
```
