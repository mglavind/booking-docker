# Django Multi-Environment Setup

This project supports three different environments:
- 🔧 **Local Development** - SQLite3, no Docker required
- 🧪 **Staging** - PostgreSQL in Docker
- 🚀 **Production** - PostgreSQL in Docker

## 📋 Prerequisites

- Python 3.13+
- Docker & Docker Compose (for staging/production)
- pip or uv package manager

## 🚀 Quick Start

### Local Development (SQLite)

```bash
# Install dependencies
cd src
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Access at: http://localhost:8000

### Staging Environment (PostgreSQL + Docker)

```bash
# Start the staging environment using the .env.staging file
docker-compose --env-file .env.staging -f docker-compose.yaml -f docker-compose.staging.yaml up -d

# View logs
docker-compose --env-file .env.staging -f docker-compose.yaml -f docker-compose.staging.yaml logs -f web

# Run migrations
docker-compose --env-file .env.staging -f docker-compose.yaml -f docker-compose.staging.yaml exec web python manage.py migrate

# Create a superuser in staging
docker-compose --env-file .env.staging -f docker-compose.yaml -f docker-compose.staging.yaml exec web python manage.py createsuperuser

# Stop the staging environment
docker-compose --env-file .env.staging -f docker-compose.yaml -f docker-compose.staging.yaml down
```

Access at: http://localhost:8001

### Production Environment (PostgreSQL + Docker)

```bash
# Start production environment
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d

# View logs
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml logs -f web

# Run migrations
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml exec web python manage.py migrate

# Stop production
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml down
```

Access at: http://localhost:8002

## 🛠️ Common Commands

### Building & Rebuilding

```bash
# Rebuild staging after code changes
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml up -d --build

# Rebuild production
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d --build

# Force recreate containers
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml up -d --force-recreate
```

### Database Management

```bash
# Run migrations in staging
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml exec web python manage.py migrate

# Run migrations in production
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml exec web python manage.py migrate

# Create database backup (staging)
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml exec db pg_dump -U staging_user staging_db > backup_staging_$(date +%Y%m%d_%H%M%S).sql

# Create database backup (production)
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml exec db pg_dump -U prod_user production_db > backup_prod_$(date +%Y%m%d_%H%M%S).sql

# Restore database from backup (staging)
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml exec -T db psql -U staging_user staging_db < backup_staging_20250101_120000.sql
```

### Shell Access

```bash
# Django shell in staging
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml exec web python manage.py shell

# Django shell in production
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml exec web python manage.py shell

# Database shell in staging
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml exec db psql -U staging_user -d staging_db

# Bash shell in container (staging)
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml exec web bash
```

### Logs & Monitoring

```bash
# Follow logs for staging
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml logs -f

# Follow only web service logs
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml logs -f web

# Show last 100 lines
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml logs --tail=100

# Check container status
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml ps
```

### Cleaning Up

```bash
# Stop and remove containers (staging)
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml down

# Stop and remove containers + volumes (⚠️ deletes database!)
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml down -v

# Remove all unused Docker resources
docker system prune -a
```

## 📝 Environment Configuration

### File Structure

```
.env.dev       # Local development (SQLite)
.env.staging   # Staging environment
.env.prod      # Production environment
```

### Required Environment Variables

#### Staging (.env.staging)
```bash
ENVIRONMENT=staging
DEBUG=True
DJANGO_SECRET_KEY=your-staging-secret-key
DJANGO_LOGLEVEL=DEBUG
DJANGO_ALLOWED_HOSTS=staging.yourdomain.com,localhost
DATABASE_NAME=staging_db
DATABASE_USERNAME=staging_user
DATABASE_PASSWORD=staging_password_here
DATABASE_HOST=db
DATABASE_PORT=5432
WEB_PORT=8001
```

#### Production (.env.prod)
```bash
ENVIRONMENT=production
DEBUG=False
DJANGO_SECRET_KEY=your-production-secret-key-very-secure
DJANGO_LOGLEVEL=WARNING
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_NAME=production_db
DATABASE_USERNAME=prod_user
DATABASE_PASSWORD=strong_production_password_here
DATABASE_HOST=db
DATABASE_PORT=5432
WEB_PORT=8002
```

## 🔒 Security Checklist

- [ ] Change all default passwords in `.env.staging` and `.env.prod`
- [ ] Generate strong `DJANGO_SECRET_KEY` for each environment
- [ ] Never commit `.env.staging` or `.env.prod` to version control
- [ ] Set `DEBUG=False` in production
- [ ] Configure proper `ALLOWED_HOSTS` for production
- [ ] Use HTTPS in production with proper SSL certificates
- [ ] Regularly backup production database
- [ ] Keep dependencies updated

### Generating a Secret Key

```python
# Run in Python shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## 🚢 Deployment Workflow

### Initial Setup

1. **Set up environment files**
   ```bash
   cp .env.example .env.staging
   cp .env.example .env.prod
   # Edit files with appropriate values
   ```

2. **Build and start staging**
   ```bash
   docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml --env-file .env.staging up -d --build
   ```

3. **Run migrations**
   ```bash
   docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml exec web python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml exec web python manage.py createsuperuser
   ```

### Updating Code

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild containers
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml --env-file .env.staging up -d --build

# 3. Run migrations
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml exec web python manage.py migrate

# 4. Collect static files (if needed)
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml exec web python manage.py collectstatic --noinput
```

### Zero-Downtime Deployment (Production)

```bash
# 1. Backup database first!
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml exec db pg_dump -U prod_user production_db > backup_before_deploy_$(date +%Y%m%d_%H%M%S).sql

# 2. Pull latest code
git pull origin main

# 3. Build new image
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml --env-file .env.prod build

# 4. Run migrations (before restarting)
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml exec web python manage.py migrate

# 5. Restart services
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml --env-file .env.prod up -d
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8001  # or 8002, 5433, 5434

# Kill the process
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check if database is healthy
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml ps

# Check database logs
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml logs db

# Restart database
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml restart db
```

### Container Won't Start

```bash
# Check logs for errors
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml logs web

# Remove and recreate containers
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml down
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml up -d --force-recreate
```

### Reset Everything (⚠️ Nuclear Option)

```bash
# This will delete ALL data!
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml down -v
docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml up -d --build
```

## 📊 Port Reference

| Environment | Web Port | Database Port |
|-------------|----------|---------------|
| Local Dev   | 8000     | N/A (SQLite)  |
| Staging     | 8001     | 5433          |
| Production  | 8002     | 5434          |

## 🎯 Makefile Shortcuts (Optional)

Create a `Makefile` in your project root for easier commands:

```makefile
.PHONY: dev staging-up staging-down staging-logs staging-shell prod-up prod-down prod-logs

dev:
	cd src && python manage.py runserver

staging-up:
	docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml up -d

staging-down:
	docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml down

staging-logs:
	docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml logs -f

staging-shell:
	docker-compose -f docker-compose.yaml -f docker-compose.staging.yaml exec web python manage.py shell

prod-up:
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d

prod-down:
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml down

prod-logs:
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml logs -f
```

Usage: `make staging-up`, `make prod-logs`, etc.

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

1. Make changes in local development
2. Test in staging environment
3. Deploy to production after verification

---

**Need help?** Check the troubleshooting section or review the Docker logs.