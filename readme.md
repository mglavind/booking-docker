# Booking System 📅

A professional Django-based booking system designed for containerized deployment.

## 🏗️ Environment Architecture
| Environment | Database | Serving via | Port |
| :--- | :--- | :--- | :--- |
| **Local** | SQLite3 | manage.py runserver | 8000 |
| **Staging** | PostgreSQL | Docker Compose | 8001 |
| **Production** | PostgreSQL | Nginx Proxy + Gunicorn | 8002 / 80 |

---

## 🔧 Development Workflow

### 1. Local Development
Best for rapid UI/UX changes and logic testing.
- `cd src`
- `pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py runserver`

### 2. Staging (Docker)
Test production-ready code with a real PostgreSQL instance locally.
- `docker compose -f docker-compose.yaml -f docker-compose.staging.yaml --env-file .env.staging up -d --build`
- `docker compose -f docker-compose.yaml -f docker-compose.prod.yaml --env-file .env.prod up -d --build`
- `docker compose exec web python manage.py migrate`

---

## 🚢 Deployment to Production (Hetzner)

### Step A: From your Local Machine
Build and push the latest image to Docker Hub.
1. `docker build -t mglavind/booking-app:latest .`
2. `docker push mglavind/booking-app:latest`

### Step B: On the Hetzner Server
Run the automation script to pull the image and update the live site.
1. `./deploy.sh`

---

## 📝 The deploy.sh Script
The `deploy.sh` script on the Hetzner server automates the following:
1. **Pulling** the latest Docker image.
2. **Restarting** containers with zero manual configuration.
3. **Migrating** the database schema automatically.
4. **Collecting** static files (essential for the **Unfold** admin theme).
5. **Permission Management** for the `./static` and `./media` folders.
6. **Nginx Reload** to ensure new assets are served immediately.

---

## 🛠️ Common Maintenance Commands

### Logs & Troubleshooting
- **Follow live logs:** `docker compose logs -f web`
- **Enter Django shell:** `docker compose exec web python manage.py shell`
- **Restart services:** `docker compose restart`

### Database Backups
- `docker compose exec db pg_dump -U mglavind production_db > backups/db_backup_$(date +%F).sql`

---

## 🔒 Security Checklist
- [ ] `DEBUG` is set to `False` in production environment.
- [ ] `ALLOWED_HOSTS` includes the production IP and domain.
- [ ] Static and Media folders are mapped to host volumes for persistence.
- [ ] Database credentials are stored in an `.env` file (never committed to Git).