# Production Deployment Guide — AI Life Manager

This guide covers deployment options for **AI Life Manager**:
- **Option A**: Modern Cloud PaaS (Vercel + Render / Railway + Neon PostgreSQL)
- **Option B**: Self-Hosted Multi-Container Docker Compose

---

## 1. Option A: Cloud PaaS Deployment

### Architecture:
- **Frontend SPA**: Hosted on [Vercel](https://vercel.com) or [Netlify](https://netlify.com)
- **Backend API & FastMCP Server**: Hosted on [Render](https://render.com), [Railway](https://railway.app), or [Fly.io](https://fly.io)
- **Database**: Managed Serverless PostgreSQL on [Neon](https://neon.tech) or [Supabase](https://supabase.com)

### Backend Environment Variables:
```env
APP_ENV=production
DEBUG=False
JWT_SECRET_KEY=generate-a-strong-random-64-character-hex-key
DATABASE_URL=postgresql+asyncpg://user:password@ep-host.neon.tech/neondb?sslmode=require
CORS_ALLOWED_ORIGINS=https://your-frontend-app.vercel.app
ANTHROPIC_API_KEY=sk-ant-... (optional, system operates in degraded mode without it)
```

### Database Migration Command:
```bash
alembic upgrade head
```

---

## 2. Option B: Docker Compose Deployment (Self-Hosted / VPS)

### Prerequisites:
- Docker 24+ & Docker Compose v2+ installed on VPS (e.g. DigitalOcean, AWS EC2, or Hetzner).

### Setup Steps:
```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-life-manager.git
cd ai-life-manager

# 2. Configure environment file
cp backend/.env.example backend/.env
# Edit backend/.env and set JWT_SECRET_KEY

# 3. Build and launch all services in background
docker compose up -d --build

# 4. Run database migrations
docker compose exec backend alembic upgrade head
```

### Verification:
- Frontend UI: `http://<your-server-ip>:5173`
- Backend API Docs: `http://<your-server-ip>:8000/docs`
- Health Check: `http://<your-server-ip>:8000/health`
