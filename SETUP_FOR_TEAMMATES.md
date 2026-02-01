# Docker Setup Guide for Teammates

## Prerequisites
- Docker Desktop installed and running
- Git installed
- At least 4GB of free RAM for Docker

## Setup Steps

### 1. Clone the Repository
```bash
git clone https://github.com/aksharabhaskar/bias_detection_platform_1.git
cd bias_detection_platform_1
```

### 2. Verify Files
Ensure these files exist in your cloned repository:
- `docker-compose.yml` (root)
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `pdf_service/Dockerfile`
- `backend/requirements.txt`
- `frontend/package.json`
- `pdf_service/requirements.txt`

### 3. Build and Run with Docker Compose
```bash
# Build all services (this may take 5-10 minutes on first run)
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Verify Services are Running
- Frontend: http://localhost (port 80)
- Backend API: http://localhost:8000
- PDF Service: http://localhost:5001

Check running containers:
```bash
docker ps
```

You should see three containers:
- `bias-detection-frontend`
- `bias-detection-backend`
- `bias-detection-pdf-service`

## Troubleshooting

### Build Fails
1. **Clear Docker cache:**
   ```bash
   docker-compose down -v
   docker system prune -a
   docker-compose build --no-cache
   ```

2. **Port conflicts:**
   If ports 80, 8000, or 5001 are already in use:
   - Stop conflicting services
   - Or modify ports in `docker-compose.yml`

3. **Docker Desktop not running:**
   - Ensure Docker Desktop is started
   - Check system tray/menu bar for Docker icon

### Common Errors

**"Cannot connect to Docker daemon"**
- Start Docker Desktop
- Wait for Docker to fully initialize

**"Port is already allocated"**
- Stop existing containers: `docker-compose down`
- Or stop other services using those ports

**"npm install fails"**
- This should be fixed now, but if issues persist:
- Check internet connection
- Try: `docker-compose build --no-cache frontend`

**"Permission denied" (Linux/Mac)**
- Add user to docker group: `sudo usermod -aG docker $USER`
- Log out and back in

## Useful Commands

```bash
# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs for specific service
docker-compose logs -f backend

# Rebuild single service
docker-compose build frontend

# Clean everything and start fresh
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## Notes
- First build will download base images (Python, Node, Nginx) - this is normal
- Node modules and Python packages are installed inside containers
- The `backend/uploads` directory is mounted as a volume for file persistence
- Changes to code require rebuilding: `docker-compose up --build`

## Need Help?
If you encounter issues:
1. Share the complete error message
2. Include output from `docker --version` and `docker-compose --version`
3. Check Docker Desktop is running and has sufficient resources allocated
