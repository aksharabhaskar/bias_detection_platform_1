# Docker Setup Guide

This guide explains how to build and run the AI Fairness Audit Dashboard using Docker.

## Architecture

The application consists of three services:
- **Frontend**: React/TypeScript application served by Nginx (Port 80)
- **Backend**: FastAPI service for fairness analysis (Port 8000)
- **PDF Service**: Flask service for generating PDF reports (Port 5001)

## Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher
- At least 4GB of available RAM
- 2GB of free disk space

## Quick Start

### 1. Build and Start All Services

```bash
docker-compose up --build
```

This command will:
- Build Docker images for all three services
- Start all containers
- Set up networking between services

### 2. Access the Application

Once all services are running, access the application at:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000/docs (Swagger UI)
- **PDF Service**: http://localhost:5001

## Docker Commands

### Build Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
docker-compose build pdf_service
```

### Start Services

```bash
# Start in foreground
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Start specific service
docker-compose up backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs

```bash
# View all logs
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs pdf_service
```

### Rebuild After Code Changes

```bash
# Rebuild and restart
docker-compose up --build

# Force rebuild without cache
docker-compose build --no-cache
```

## Service Details

### Backend Service
- **Image**: Python 3.10 slim
- **Port**: 8000
- **Framework**: FastAPI
- **Volume**: ./backend/uploads (for uploaded datasets)

### Frontend Service
- **Image**: Node 18 (build) + Nginx Alpine (runtime)
- **Port**: 80
- **Build**: Multi-stage build for optimized size
- **Reverse Proxy**: Nginx proxies API requests to backend

### PDF Service
- **Image**: Python 3.10 slim
- **Port**: 5001
- **Framework**: Flask
- **Purpose**: Generate PDF reports with matplotlib charts

## Environment Variables

You can configure services using environment variables in `.env` file:

```env
# Backend
BACKEND_PORT=8000
PDF_SERVICE_URL=http://pdf_service:5001

# PDF Service
PDF_SERVICE_PORT=5001

# Frontend
FRONTEND_PORT=80
```

## Troubleshooting

### Port Already in Use

If ports are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "8080:80"  # Change frontend to port 8080
```

### Permission Issues with Uploads

If you encounter permission errors with the uploads volume:

```bash
# Linux/Mac
sudo chown -R $USER:$USER backend/uploads

# Windows (run PowerShell as Administrator)
icacls backend\uploads /grant Everyone:F /T
```

### Out of Memory

Increase Docker Desktop memory allocation:
- Docker Desktop → Settings → Resources → Memory
- Allocate at least 4GB

### Container Won't Start

Check logs for specific error:
```bash
docker-compose logs [service-name]
```

Common issues:
- Missing dependencies in requirements.txt or package.json
- Syntax errors in code
- Port conflicts

## Production Deployment

For production deployment:

1. **Use environment-specific configuration**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Enable HTTPS with SSL certificates**

3. **Set up proper secrets management**

4. **Configure resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

5. **Use container orchestration** (Kubernetes, Docker Swarm, etc.)

## Maintenance

### Update Dependencies

```bash
# Backend
docker-compose exec backend pip install --upgrade -r requirements.txt

# Frontend (requires rebuild)
docker-compose build frontend
```

### Clean Up

```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune

# Remove all unused resources
docker system prune -a
```

## Development Workflow

For active development, you can mount source code as volumes:

```yaml
# Add to docker-compose.yml under backend service
volumes:
  - ./backend:/app
  - ./backend/uploads:/app/uploads
```

Then use hot-reload:
```bash
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Verify all services are healthy: `docker-compose ps`
- Rebuild from scratch: `docker-compose down -v && docker-compose up --build`
