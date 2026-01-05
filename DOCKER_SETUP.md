# BankingNewApp - Docker Setup Guide

Complete guide for running the BankingNewApp using Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available
- Ports 3000, 5000, 5432, 5050 available

## Quick Start

### 1. Clone and Navigate

```bash
cd Migration-Framework
```

### 2. Start All Services

```bash
docker-compose up -d
```

This command starts:
- **PostgreSQL** database on port `5432`
- **FastAPI** backend on port `8000`
- **Next.js** frontend on port `3000`
- **pgAdmin** on port `5050` (optional)

### 3. Verify Services Are Running

```bash
docker-compose ps
```

You should see all services with status "Up".

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (admin@banking.com / admin123)

## Service Details

### PostgreSQL Database

- **Container**: `banking_postgres`
- **Port**: 5432
- **Database**: `banking_db`
- **User**: `bankingapp`
- **Password**: `bankingapp123`
- **Data**: Persisted in Docker volume `postgres_data`

### FastAPI Backend

- **Container**: `banking_backend`
- **Port**: 8000
- **Auto-reload**: Enabled (development mode)
- **Source**: Mounted from `./src/backend`
- **Migrations**: Run automatically on startup

### Next.js Frontend

- **Container**: `banking_frontend`
- **Port**: 3000
- **Hot-reload**: Enabled
- **Source**: Mounted from `./src/frontend`
- **API URL**: Configured to http://localhost:8000

### pgAdmin (Database Management)

- **Container**: `banking_pgadmin`
- **Port**: 5050
- **Email**: admin@banking.com
- **Password**: admin123

**To connect to database in pgAdmin**:
1. Open http://localhost:5050
2. Login with credentials above
3. Right-click "Servers" → "Register" → "Server"
4. General tab: Name = "Banking DB"
5. Connection tab:
   - Host: `postgres`
   - Port: `5432`
   - Database: `banking_db`
   - Username: `bankingapp`
   - Password: `bankingapp123`

## Common Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes database data)
```bash
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Restart a service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Rebuild services (after code changes)
```bash
docker-compose up -d --build
```

### Execute commands in containers
```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# PostgreSQL shell
docker-compose exec postgres psql -U bankingapp -d banking_db
```

## Database Operations

### Run migrations manually
```bash
docker-compose exec backend alembic upgrade head
```

### Create a new migration
```bash
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Rollback migration
```bash
docker-compose exec backend alembic downgrade -1
```

### Seed database with sample data
```bash
docker-compose exec backend python scripts/seed_data.py
```

## Development Workflow

### Making Backend Changes

1. Edit files in `src/backend/`
2. Changes auto-reload thanks to `--reload` flag
3. Check logs: `docker-compose logs -f backend`

### Making Frontend Changes

1. Edit files in `src/frontend/`
2. Next.js hot-reload handles updates automatically
3. Check logs: `docker-compose logs -f frontend`

### Database Schema Changes

1. Edit models in `src/backend/app/models/`
2. Generate migration:
   ```bash
   docker-compose exec backend alembic revision --autogenerate -m "add_field"
   ```
3. Apply migration:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

## Troubleshooting

### Port Already in Use

If you see "port is already allocated":

```bash
# Find what's using the port (example for port 5432)
lsof -i :5432

# Stop the conflicting service or change port in docker-compose.yml
```

### Database Connection Refused

```bash
# Check if postgres is healthy
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Backend Not Starting

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Database not ready → Wait for health check
# - Migration failed → Check migration files
# - Port conflict → Change port in docker-compose.yml
```

### Frontend Build Errors

```bash
# Rebuild node_modules
docker-compose down
docker-compose up -d --build frontend

# Or manually:
docker-compose exec frontend npm install
```

### Clear Everything and Start Fresh

```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d --build
```

## Environment Variables

### Backend (.env)

Create `src/backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://bankingapp:bankingapp123@postgres:5432/banking_db
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)

Create `src/frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Production Deployment

For production, you need to:

1. **Change passwords and secrets**
   - Update `SECRET_KEY` in backend
   - Change database password
   - Update pgAdmin credentials

2. **Disable development features**
   - Remove `--reload` from backend command
   - Build frontend: `npm run build && npm start`
   - Remove volume mounts for source code

3. **Add reverse proxy**
   - Use Nginx for SSL termination
   - Route traffic through single domain

4. **Configure backups**
   - Automated database backups
   - Volume backups

5. **Update docker-compose.yml**
   - See `docker-compose.prod.yml` for production config

## Health Checks

All services have health checks:

```bash
# Check service health
docker-compose exec backend curl http://localhost:8000/health
docker-compose exec frontend curl http://localhost:3000/api/health
docker-compose exec postgres pg_isready -U bankingapp
```

## Performance Tuning

### Increase PostgreSQL resources

Edit `docker-compose.yml`:

```yaml
postgres:
  environment:
    POSTGRES_SHARED_BUFFERS: 256MB
    POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
```

### Limit container resources

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '0.50'
        memory: 512M
```

## Support

For issues:
1. Check logs: `docker-compose logs -f [service]`
2. Verify all containers are running: `docker-compose ps`
3. Check Docker resources: `docker stats`
4. Review this document's troubleshooting section

## Architecture

```
┌─────────────────┐
│   Browser       │
└────────┬────────┘
         │
    ┌────▼─────────────────┐
    │  Frontend (Next.js)  │
    │   localhost:3000     │
    └────────┬─────────────┘
             │
        ┌────▼──────────────┐
        │  Backend (FastAPI)│
        │  localhost:8000   │
        └────────┬──────────┘
                 │
        ┌────────▼────────────┐
        │  PostgreSQL         │
        │  localhost:5432     │
        └─────────────────────┘
```

All services run in isolated Docker containers connected via `banking_network`.
