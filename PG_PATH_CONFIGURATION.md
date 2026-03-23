# PostgreSQL Configuration Options - Quick Reference

## Two Ways to Configure PostgreSQL

### Option 1: Full Connection String (PG_PATH) - EASIEST
Use a single connection string variable. Perfect for cloud platforms like Render, Railway, Heroku.

```env
# Single line configuration
PG_PATH=postgresql://ticket_user:your_password@dpg-xxxxx.render.com:5432/ticket_db

# Or with internal Render URL (faster, same region)
PG_PATH=postgresql://ticket_user:your_password@dpg-xxxxx.internal:5432/ticket_db

# Examples from different platforms:
# Render: postgresql://user:pass@dpg-xxxxx.render.com:5432/dbname
# Railway: postgresql://user:pass@containers-us-west-1.railway.app:5432/dbname
# Heroku: postgresql://user:pass@ec2-12-34-567-890.compute-1.amazonaws.com:5432/dbname
```

### Option 2: Individual Components
Break down the connection into separate variables.

```env
PG_HOST=localhost
PG_USER=ticket_user
PG_PASSWORD=your_password
PG_DATABASE=ticket_db
PG_PORT=5432
```

---

## Environment Variable Priority

**PG_PATH takes precedence** over individual components. If both are set, PG_PATH is used.

```
PG_PATH (if set) ──→ Use this
    ↓
PG_HOST + PG_USER (if set) ──→ Use individual components
    ↓
DB_TYPE=sqlite (default)
```

---

## Configuration Examples

### Local Development
```env
# Option 1: Connection string
PG_PATH=postgresql://postgres:password@localhost:5432/ticket_db

# Option 2: Individual components
PG_HOST=localhost
PG_USER=postgres
PG_PASSWORD=password
PG_DATABASE=ticket_db
PG_PORT=5432
DB_TYPE=postgresql
```

### Render Deployment
```env
# Just paste the connection string from Render dashboard
PG_PATH=postgresql://ticket_user:abc123xyz@dpg-ch1234567890ab-a.render.com:5432/ticket_db

# Or use internal URL for better performance
PG_PATH=postgresql://ticket_user:abc123xyz@dpg-ch1234567890ab-a.internal:5432/ticket_db
```

### Railway Deployment
```env
PG_PATH=postgresql://postgres:password@containers-us-west-1.railway.app:1234/railway
```

### Heroku Deployment
```env
# Heroku sets DATABASE_URL automatically, but you can override:
PG_PATH=postgresql://user:password@ec2-12-34-567-890.compute-1.amazonaws.com:5432/dbname
```

### Docker Compose
```env
PG_HOST=postgres_service
PG_USER=ticket_user
PG_PASSWORD=secure_password
PG_DATABASE=ticket_db
PG_PORT=5432
```

### Production Server (Self-Hosted)
```env
PG_HOST=db.production.example.com
PG_USER=ticket_user
PG_PASSWORD=very_secure_password_123
PG_DATABASE=ticket_db
PG_PORT=5432
DB_TYPE=postgresql
```

---

## Supported URL Formats

The PG_PATH parser handles these formats:

```
postgresql://user:password@host:port/database
postgresql://user:password@host/database (default port 5432)
postgresql://user@host:port/database (no password)
postgresql://host:port/database (no auth)
psql://... (alternative protocol name)
postgres://... (legacy protocol name)
```

---

## How It Works (Behind the Scenes)

When you set `PG_PATH`:

```python
# Your .env
PG_PATH=postgresql://ticket_user:mypass123@db.example.com:5432/ticket_db

# Parser extracts:
pg_host = "db.example.com"       # from hostname
pg_user = "ticket_user"          # from username
pg_password = "mypass123"        # from password
pg_database = "ticket_db"        # from path (after /)
pg_port = 5432                   # from port
```

---

## Tips & Best Practices

### ✅ DO:
- Use `PG_PATH` for cloud deployments (cleaner, one variable)
- Use individual components for local/Docker setup (easier to read)
- Keep `.env` file in `.gitignore` (never commit credentials)
- Use secure passwords (20+ characters, mixed case, numbers, symbols)
- Rotate passwords periodically in production

### ❌ DON'T:
- Commit `.env` with real passwords to GitHub
- Use simple passwords in production
- Share connection strings over unencrypted channels
- Mix PG_PATH and individual components (confusing)
- Hardcode database credentials

---

## Troubleshooting

### Error: "could not connect to server"
```
Check:
1. PG_PATH or individual components set correctly
2. PostgreSQL service is running
3. Firewall allows connections on port 5432
4. Credentials are correct
5. For cloud: Use internal URL if available (faster)
```

### Error: "password authentication failed"
```
Check:
1. PG_PASSWORD matches actual password
2. No special characters breaking the URL
3. If URL has special chars, URL-encode them:
   @ = %40, # = %23, % = %25, etc.
```

### Connection string has special characters
If your password has special chars, either:

**Option A:** Use individual components instead
```env
PG_HOST=localhost
PG_USER=ticket_user
PG_PASSWORD=p@ss#word%123
PG_DATABASE=ticket_db
```

**Option B:** URL-encode in connection string
```env
PG_PATH=postgresql://ticket_user:p%40ss%23word%25123@localhost:5432/ticket_db
```

---

## Quick Migration Guide

### Switching from Individual to PG_PATH
```bash
# Old way (.env)
PG_HOST=localhost
PG_USER=ticket_user
PG_PASSWORD=mypass
PG_DATABASE=ticket_db
PG_PORT=5432

# New way (.env) - same effect, one variable
PG_PATH=postgresql://ticket_user:mypass@localhost:5432/ticket_db

# Remove old variables (optional, but cleaner)
```

### Switching from SQLite to PostgreSQL
```bash
# Step 1: Set PG_PATH
PG_PATH=postgresql://user:pass@host:5432/database

# Step 2: Application auto-detects and uses PostgreSQL
# No code changes needed!

# Optional: Migrate data (see migration guide)
```

---

## Platform-Specific Guides

### Render
1. Create PostgreSQL database on Render dashboard
2. Copy connection string from Render dashboard
3. Add to `.env`: `PG_PATH=<connection_string>`
4. Deploy!

### Railway
1. Create PostgreSQL plugin
2. Copy DATABASE_URL
3. Add to `.env`: `PG_PATH=$DATABASE_URL`
4. Deploy!

### Docker Compose
```yaml
version: '3'
services:
  app:
    environment:
      - PG_HOST=postgres
      - PG_USER=ticket_user
      - PG_PASSWORD=secure_pass
      - PG_DATABASE=ticket_db
      - PG_PORT=5432
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ticket_db
      POSTGRES_USER: ticket_user
      POSTGRES_PASSWORD: secure_pass
```

---

## Summary

| Scenario | Recommendation |
|----------|----------------|
| Local development | Individual components |
| Docker/containers | Individual components or PG_PATH |
| Render | PG_PATH (copy-paste from dashboard) |
| Railway | PG_PATH (use $DATABASE_URL) |
| Production server | Individual components (more control) |
| Multiple environments | PG_PATH (simpler .env files) |

Both options work perfectly - choose what's easiest for your workflow! 🚀
