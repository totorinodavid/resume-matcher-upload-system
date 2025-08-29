# Neon Local Connect Setup für Resume Matcher
# PostgreSQL-only Development und Production

## Voraussetzungen

1. **Neon Account**: https://neon.tech (kostenlos)
2. **Neon CLI**: `npm install -g neonctl` oder `curl -sSfL https://neon.tech/install | bash`
3. **Python Dependencies**: `asyncpg`, `psycopg2-binary`

## Lokale Entwicklung mit Neon Local Connect

### 1. Neon Local Connect einrichten

```bash
# Neon CLI installieren
npm install -g neonctl

# Bei Neon anmelden
neonctl auth

# Lokale Verbindung zu deinem Neon-Projekt starten
neonctl proxy --connection-string postgres://postgres:password@localhost:5432/resume_matcher_dev
```

### 2. Lokale Umgebung konfigurieren

```bash
# .env.development erstellen
cp .env.development apps/backend/.env

# Environment-Variablen setzen:
DATABASE_URL=postgres://postgres:password@localhost:5432/resume_matcher_dev
SYNC_DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/resume_matcher_dev  
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/resume_matcher_dev
```

### 3. PostgreSQL Dependencies installieren

```bash
cd apps/backend

# Python Dependencies für PostgreSQL
uv add asyncpg psycopg2-binary

# Oder mit pip
pip install asyncpg psycopg2-binary
```

### 4. Database Setup ausführen

```bash
# PostgreSQL Setup und Migrations
python setup_postgres.py --mode development

# Oder manuell:
uv run alembic upgrade head
```

### 5. Backend starten

```bash
# Mit UV
uv run uvicorn app.main:app --reload --port 8000

# Oder mit Python
python -m uvicorn app.main:app --reload --port 8000
```

## Production Deployment mit Neon

### 1. Neon Production Database erstellen

```bash
# Neues Neon-Projekt für Production
neonctl projects create --name resume-matcher-production

# Connection String für Production abrufen
neonctl connection-string --pooled
```

### 2. Production Environment konfigurieren

```bash
# .env.production updaten mit echter Neon Connection:
DATABASE_URL=postgres://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/main?sslmode=require
SYNC_DATABASE_URL=postgresql+psycopg://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/main?sslmode=require
ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/main?ssl=require
```

### 3. Production Migrations ausführen

```bash
# Production Database Setup
python setup_postgres.py --mode production --skip-seed

# Oder mit Alembic:
DATABASE_URL="postgres://..." uv run alembic upgrade head
```

## Entwicklungs-Workflow

### Lokale Entwicklung starten

```bash
# Terminal 1: Neon Local Connect
neonctl proxy --connection-string postgres://postgres:password@localhost:5432/resume_matcher_dev

# Terminal 2: Backend
cd apps/backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 3: Frontend  
cd apps/frontend
npm run dev
```

### Database Migrations erstellen

```bash
# Neue Migration erstellen
uv run alembic revision --autogenerate -m "Add new feature"

# Migration anwenden (lokal)
uv run alembic upgrade head

# Migration anwenden (production)
DATABASE_URL="postgres://..." uv run alembic upgrade head
```

### PostgreSQL Features nutzen

```python
# In deinen Models: JSONB für flexible Daten
from sqlalchemy.dialects.postgresql import JSONB

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    # PostgreSQL JSONB für strukturierte Daten
    metadata = Column(JSONB, default={})
    skills = Column(JSONB, default=[])
    
# In Queries: PostgreSQL-spezifische Features
from sqlalchemy import text

# JSONB Queries
query = text("""
    SELECT * FROM resumes 
    WHERE metadata->>'status' = :status
    AND skills @> :required_skills::jsonb
""")

result = await session.execute(query, {
    "status": "processed",
    "required_skills": ["Python", "FastAPI"]
})
```

## Troubleshooting

### Connection Issues

```bash
# Neon Connection testen
neonctl test-connection

# Lokale PostgreSQL Connection testen
psql -h localhost -p 5432 -U postgres -d resume_matcher_dev

# Python Connection testen
python -c "
import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect('postgres://postgres:password@localhost:5432/resume_matcher_dev')
    version = await conn.fetchval('SELECT version()')
    print(f'Connected: {version}')
    await conn.close()

asyncio.run(test())
"
```

### Common Errors

1. **"database does not exist"**:
   ```bash
   python setup_postgres.py --mode development
   ```

2. **"asyncpg connection failed"**:
   ```bash
   # Neon Local Connect neu starten
   neonctl proxy --connection-string postgres://postgres:password@localhost:5432/resume_matcher_dev
   ```

3. **"psycopg2 not found"**:
   ```bash
   uv add psycopg2-binary
   ```

## Vorteile von PostgreSQL + Neon

✅ **Konsistenz**: Gleiche Database in Development und Production  
✅ **Features**: JSONB, CTEs, Advanced Indexing  
✅ **Performance**: Connection Pooling, Query Optimization  
✅ **Backup**: Automatische Backups in Neon  
✅ **Scaling**: Neon Auto-Scaling in Production  
✅ **Security**: SSL/TLS, Role-based Access Control  

## Nächste Schritte

1. **Neon Local Connect starten**: `neonctl proxy ...`
2. **Dependencies installieren**: `uv add asyncpg psycopg2-binary`  
3. **Database setup**: `python setup_postgres.py --mode development`
4. **Backend starten**: `uv run uvicorn app.main:app --reload`
5. **Tests ausführen**: `uv run pytest` (alle nutzen PostgreSQL)

**🎯 Ab sofort: Kein SQLite mehr - nur PostgreSQL für konsistente Entwicklung!**
