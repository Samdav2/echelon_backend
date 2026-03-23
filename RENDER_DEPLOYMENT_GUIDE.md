# Deploying to Render - Complete Guide

## Overview
Render is a modern cloud platform for deploying web services and databases. This guide covers deploying your FastAPI backend with PostgreSQL on Render.

---

## Step 1: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (recommended for easier deployments)
3. Authorize Render to access your GitHub repositories

---

## Step 2: Create PostgreSQL Database on Render

### Create Database:
1. Dashboard → New → PostgreSQL
2. **Name**: `ticket-db` (or your choice)
3. **Database**: `ticket_db`
4. **User**: `ticket_user`
5. **Region**: Choose closest to your users (e.g., Frankfurt for EU)
6. **Plan**: Free tier for testing, Starter for production
7. Click **Create Database**

### Save Connection Details:
After creation, Render shows:
- **Host**: `dpg-xxxxx.render.com`
- **Port**: `5432`
- **Database**: `ticket_db`
- **User**: `ticket_user`
- **Password**: Shown once - save it!

**Internal Connection String** (for services in same region):
```
postgresql://ticket_user:PASSWORD@dpg-xxxxx.internal:5432/ticket_db
```

**External Connection String** (for external connections):
```
postgresql://ticket_user:PASSWORD@dpg-xxxxx.render.com:5432/ticket_db
```

---

## Step 3: Deploy Backend Service on Render

### Create Web Service:
1. Dashboard → New → Web Service
2. **Connect Repository**: Select your GitHub repo (feranmiba/tick)
3. **Name**: `ticket-backend`
4. **Runtime**: Python
5. **Branch**: main
6. **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
7. **Start Command**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Configure Environment Variables:

In the **Environment** section, add:

```env
# Database
DB_TYPE=postgresql
PG_HOST=dpg-xxxxx.internal
PG_USER=ticket_user
PG_PASSWORD=your_password_here
PG_DATABASE=ticket_db
PG_PORT=5432

# Application
DEBUG=False
PORT=10000

# JWT
JWT_SECRET_KEY=your-very-secure-random-string-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://your-app.render.com

# Cloudinary (if using image uploads)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Mailjet (if using email)
MAILJET_API_KEY=your_api_key
MAILJET_SECRET_KEY=your_secret_key
```

### Select Plan:
- **Free**: Good for testing/demo
- **Starter** ($7/month): Good for production

### Deploy:
Click **Create Web Service** - Render will start deploying!

---

## Step 4: Verify Deployment

### Check Deployment Logs:
1. Service Dashboard → Logs tab
2. Look for: `Application startup complete`

### Test API:
```bash
curl https://your-service-name.onrender.com/health
```

---

## Step 5: Setup Auto-Deployment

### Enable GitHub Integration:
1. Service Dashboard → Settings
2. **Auto-Deploy**: Turn ON
3. Select trigger branch: `main`
4. Now every push to main auto-deploys!

### Skip Deployment for Docs:
Add to `.gitignore` if not already:
```
*.md
__pycache__/
*.pyc
.env
```

---

## Step 6: Database Backups

### Render's Built-in Backups:
- Free tier: 1 backup (7 days)
- Starter+: Automatic daily backups (7 days retention)

### Manual Backup:
1. Database Dashboard → Settings
2. Click **Create Manual Backup**

### Restore from Backup:
1. Database Dashboard → Backups
2. Click backup → **Restore**

---

## Step 7: Monitor Service

### Logs:
Service Dashboard → Logs tab - real-time logs

### Metrics:
Service Dashboard → Metrics tab - CPU, Memory, Requests

### Database Metrics:
Database Dashboard → Metrics tab

---

## Step 8: Custom Domain (Optional)

### Add Custom Domain to Backend:
1. Service Dashboard → Settings
2. **Custom Domains** → Add domain
3. Point your domain to: `your-service.onrender.com`
4. Update CORS in `.env` with new domain

---

## Step 9: Environment-Specific Setup

### For Production:
```env
DB_TYPE=postgresql
DEBUG=False
JWT_SECRET_KEY=generate-random-256-bit-key
ALLOWED_ORIGINS=https://your-domain.com
```

### For Testing:
```env
DB_TYPE=postgresql
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,https://test.yourdomain.com
```

---

## Troubleshooting

### Build Failed:
**Error**: `pip install failed`
- Check `requirements.txt` is in repo root
- Verify all dependencies are compatible with Python 3.9+
- Try local install first: `pip install -r requirements.txt`

### Connection to Database Failed:
**Error**: `could not connect to server: No address associated with hostname`
- Use **Internal** connection string (dpg-xxxxx.internal)
- Verify database is in same region as service
- Check PG_PASSWORD is correct (special chars need escaping)

### 502 Bad Gateway:
**Error**: Service crashed
- Check logs for errors
- Verify environment variables are set
- Test locally: `uvicorn app.main:app --reload`

### Slow Deployments:
- First deployment slower (installing dependencies)
- Subsequent deployments faster (cached layers)
- Render spins down free tier after 15 min inactivity

### Database Connection Pool Full:
**Error**: `too many connections`
- Increase max_connections (Starter+ plan)
- Reduce connection pool size in app
- Use connection pooling (PgBouncer)

---

## Production Checklist

- [ ] Enable auto-deploy on GitHub
- [ ] Set `DEBUG=False`
- [ ] Use strong JWT_SECRET_KEY
- [ ] Configure ALLOWED_ORIGINS properly
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set up email service (Mailjet)
- [ ] Test all endpoints after deployment
- [ ] Monitor logs for errors
- [ ] Setup backup retention
- [ ] Configure custom domain
- [ ] Add monitoring/alerting

---

## Cost Estimation

### Free Tier:
- Web Service: Free (limited to 750 hours/month = ~1 service continuous)
- Database: Free (limited capacity)

### Production Tier:
- Web Service: $7/month (pay-as-you-go, discounted if committed)
- Database: $15/month (Starter PostgreSQL)
- **Total**: ~$22/month for basic production setup

---

## Database Connection Pool Configuration

For high-traffic apps, optimize connection pooling:

### In your app code (if needed):
```python
# app/core/db_connector.py example
pool_pre_ping=True  # Verify connections before use
pool_recycle=3600   # Recycle connections every hour
pool_size=5         # Number of connections to maintain
max_overflow=10     # Max extra connections
```

---

## Scale to Production

### Upgrade Web Service:
1. Service Dashboard → Settings
2. Change Plan to **Standard** or **Pro**
3. Increase Instances for load balancing

### Upgrade Database:
1. Database Dashboard → Settings
2. Change Plan to **Standard** or **Pro**
3. Increase compute/memory as needed

### Add CDN for Images (Cloudinary):
Already configured! Just ensure CLOUDINARY env vars are set.

---

## Monitoring & Alerts

### Setup Email Alerts:
1. Account Settings → Notifications
2. Enable alerts for:
   - Deployment failures
   - Service failures
   - High memory usage

---

## Update Application

### Deploy New Version:
```bash
# Make changes locally
git add .
git commit -m "Update features"
git push origin main
```

Render auto-deploys (if enabled) within 1-2 minutes!

### Rollback to Previous Version:
1. Service Dashboard → Events
2. Find previous deployment
3. Click **Redeploy**

---

## Quick Deployment Summary

```bash
# 1. Prepare repo
git add .
git commit -m "Ready for Render"
git push

# 2. On Render:
# - Create PostgreSQL database
# - Note internal connection string
# - Create Web Service
# - Configure env variables with DB connection
# - Deploy!

# 3. Test
curl https://your-service.onrender.com/health

# 4. Enable auto-deploy
# Service Settings → Auto-Deploy → Enable

# 5. Monitor
# Check logs, metrics, database status
```

---

## Important Notes

### About Render Free Tier:
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- For continuous availability, upgrade to paid plan
- Not recommended for production APIs

### Database Notes:
- PostgreSQL on Render is fully managed
- Automatic backups (with paid plans)
- SSL connections by default
- 90 days data retention on free tier

### Deployment Limits:
- Build timeout: 30 minutes
- Max log size: Kept for 1 month
- Database size: Depends on plan

---

## Support & Documentation

- **Render Docs**: https://render.com/docs
- **PostgreSQL**: https://render.com/docs/databases
- **Deployments**: https://render.com/docs/deploy-service
- **Environment Variables**: https://render.com/docs/environment-variables
