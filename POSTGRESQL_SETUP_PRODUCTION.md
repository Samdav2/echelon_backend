# PostgreSQL Setup Guide for Live Server

## Step 1: Install PostgreSQL on Live Server

### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### On CentOS/RHEL:
```bash
sudo yum install postgresql-server postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

## Step 2: Create Database & User

### Login to PostgreSQL:
```bash
sudo -u postgres psql
```

### Create Database:
```sql
CREATE DATABASE ticket_db;
```

### Create User (with secure password):
```sql
CREATE USER ticket_user WITH PASSWORD 'your_secure_password_here';
```

### Grant Privileges:
```sql
GRANT ALL PRIVILEGES ON DATABASE ticket_db TO ticket_user;

-- Connect to the database
\c ticket_db

-- Grant schema privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO ticket_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ticket_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ticket_user;
```

### Exit PostgreSQL:
```sql
\q
```

---

## Step 3: Configure PostgreSQL Access (pg_hba.conf)

### Edit PostgreSQL configuration:
```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

Find and update (or add) these lines:
```
listen_addresses = '*'
port = 5432
```

### Edit PostgreSQL client authentication:
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

Add this line at the end (for TCP/IP connections):
```
# Allow connections from your app server IP
host    ticket_db    ticket_user    YOUR_APP_SERVER_IP/32    md5
```

Or allow from anywhere (less secure):
```
host    ticket_db    ticket_user    0.0.0.0/0    md5
```

### Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

## Step 4: Set Environment Variables on Live Server

### Update `.env` file:
```bash
# Database Type
DB_TYPE=postgresql

# PostgreSQL Configuration
PG_HOST=localhost          # or your PostgreSQL server IP
PG_USER=ticket_user
PG_PASSWORD=your_secure_password_here
PG_DATABASE=ticket_db
PG_PORT=5432

# Disable MySQL config (optional)
# MYSQL_HOST=
# MYSQL_USER=
# MYSQL_PASSWORD=
# MYSQL_DATABASE=
```

### Set permissions on `.env`:
```bash
chmod 600 .env
```

---

## Step 5: Update Application Dependencies

### Install PostgreSQL driver:
```bash
source .venv/bin/activate
pip install psycopg2-binary
```

### Update `requirements.txt`:
```bash
pip freeze | grep psycopg2 >> requirements.txt
```

---

## Step 6: Test Connection

### Test PostgreSQL connection locally:
```bash
psql -h localhost -U ticket_user -d ticket_db -c "SELECT 1;"
```

### From application server (if different):
```bash
psql -h POSTGRES_SERVER_IP -U ticket_user -d ticket_db -c "SELECT 1;"
```

---

## Step 7: Initialize Database Tables

### From app directory:
```bash
cd /path/to/app
source .venv/bin/activate
python -c "from app.core.db_connector import db; db.create_all()"
```

Or when you start the app, it will auto-initialize (if enabled).

---

## Step 8: Update Startup Script

### Edit `startup.sh`:
```bash
#!/bin/bash

# Set environment
export DB_TYPE=postgresql
export PG_HOST=localhost
export PG_USER=ticket_user
export PG_PASSWORD=your_secure_password_here
export PG_DATABASE=ticket_db
export PG_PORT=5432

# Start application
cd /path/to/app
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Make executable:
```bash
chmod +x startup.sh
```

---

## Step 9: Setup PostgreSQL Backup

### Create backup script:
```bash
#!/bin/bash
# backup_postgres.sh

BACKUP_DIR="/var/backups/postgresql"
DB_NAME="ticket_db"
DB_USER="ticket_user"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"

mkdir -p $BACKUP_DIR
pg_dump -U $DB_USER -d $DB_NAME > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

### Make executable:
```bash
chmod +x backup_postgres.sh
```

### Schedule backup with cron (daily at 2 AM):
```bash
sudo crontab -e
```

Add this line:
```
0 2 * * * /path/to/backup_postgres.sh
```

---

## Step 10: Monitor PostgreSQL

### Check PostgreSQL status:
```bash
sudo systemctl status postgresql
```

### View PostgreSQL logs:
```bash
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Check active connections:
```sql
psql -U postgres -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

---

## Step 11: Performance Tuning (Production)

### Edit PostgreSQL configuration:
```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

### Recommended production settings:
```
# Memory
shared_buffers = 256MB              # 25% of system RAM
effective_cache_size = 1GB          # 50-75% of system RAM
work_mem = 16MB
maintenance_work_mem = 64MB

# Connections
max_connections = 200
max_prepared_transactions = 100

# Query performance
random_page_cost = 1.1              # for SSD
effective_io_concurrency = 200

# WAL (Write-Ahead Logging)
wal_buffers = 16MB
max_wal_size = 2GB

# Checkpoints
checkpoint_completion_target = 0.9
wal_recycle = on
```

### Restart after changes:
```bash
sudo systemctl restart postgresql
```

---

## Database Type Auto-Detection

The application will automatically detect which database to use based on this priority:

1. **If `DB_TYPE=postgresql` is set** → Use PostgreSQL
2. **Else if `PG_HOST` is configured** → Use PostgreSQL
3. **Else if `MYSQL_HOST` is configured** → Use MySQL
4. **Else** → Use SQLite (fallback)

---

## Troubleshooting

### Connection refused error:
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify firewall allows port 5432: `sudo ufw allow 5432`
- Check pg_hba.conf has correct entry
- Verify credentials in `.env`

### Permission denied error:
```
FATAL: Ident authentication failed
```

**Solution:**
- Edit `pg_hba.conf` and change `ident` to `md5`
- Restart: `sudo systemctl restart postgresql`

### Database already exists:
```
ERROR: database "ticket_db" already exists
```

**Solution:** Connect and use existing database (OK for production)

### Connection pool errors:
**Solution:** Increase `max_connections` in postgresql.conf

---

## Security Best Practices

1. **Use strong passwords** for PostgreSQL users
2. **Restrict network access** using firewall rules
3. **Use SSL/TLS** for remote connections:
   ```bash
   psql -h remote_server -U user -d db --ssl=require
   ```
4. **Keep PostgreSQL updated**:
   ```bash
   sudo apt update && sudo apt upgrade postgresql*
   ```
5. **Regular backups** (see Step 9)
6. **Monitor logs** for suspicious activity
7. **Use connection pooling** (pgBouncer) for many connections

---

## Quick Start Summary

```bash
# 1. Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# 2. Create database and user
sudo -u postgres psql
# (in psql)
CREATE DATABASE ticket_db;
CREATE USER ticket_user WITH PASSWORD 'secure_pass';
GRANT ALL PRIVILEGES ON DATABASE ticket_db TO ticket_user;
\q

# 3. Update .env
DB_TYPE=postgresql
PG_HOST=localhost
PG_USER=ticket_user
PG_PASSWORD=secure_pass
PG_DATABASE=ticket_db

# 4. Install driver
pip install psycopg2-binary

# 5. Start app
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Switching Back to MySQL

If you need to switch back to MySQL:

```bash
# Update .env
DB_TYPE=mysql
MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_pass
MYSQL_DATABASE=your_mysql_db
```

Application will automatically detect and use MySQL instead.
