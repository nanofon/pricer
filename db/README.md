# Storage Service

This directory contains the Docker configuration for the PostgreSQL database used by the Pricer application.

## Prerequisites

- Docker Desktop installed and running.

## Quick Start

1. **Navigate to the directory:**

   ```powershell
   cd storage
   ```

2. **Start the database:**

   ```powershell
   docker-compose up -d --build
   ```

3. **Stop the database:**
   ```powershell
   docker-compose down
   ```

## Access Details

The PostgreSQL container is accessible from the host machine at:

- **Host:** `127.0.0.1`
- **Port:** `5433` (Remapped from internal 5432 to avoid local conflicts)
- **User:** `postgres`
- **Password:** `password`
- **Database:** `pricer`

## Configuration

- **Definitions**: `docker-compose.yml`
- **Dockerfile**: `Dockerfile.db`
- **Data Volume**: `postgres_data` (Persists data between restarts)

## ML Worker

- **Definitions**: `ml_worker/docker-compose.yml`
- **Dockerfile**: `ml_worker/Dockerfile`
- **Data Volume**: `ml_worker_data` (Persists data between restarts)

## Access data

docker exec -it pricer-db-1 psql -U postgres -d pricer

docker logs --tail=50 pricer-db-1
docker logs --tail=50 pricer-crawler-1
docker logs --tail=50 pricer-embedder-1
docker logs --tail=50 pricer-ml-1
docker logs --tail=50 pricer-api-1
docker logs --tail=50 pricer-frontend-1
