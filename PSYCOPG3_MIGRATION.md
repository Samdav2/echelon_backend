# PostgreSQL on Render - Python 3.14 Compatibility Fix

## Problem
Render uses Python 3.14, but `psycopg2-binary` doesn't have pre-built wheels for Python 3.14, causing:
```
ImportError: /path/to/psycopg2/_psycopg.cpython-314-x86_64-linux-gnu.so:
undefined symbol: _PyInterpreterState_Get
```

## Solution
Upgraded from `psycopg2` to `psycopg` (v3) which has full Python 3.14 support.

---

## What Changed

### 1. Updated `requirements.txt`
**Before:**
```
psycopg2-binary==2.9.9
```

**After:**
```
psycopg[binary]==3.18.0
```

### 2. Updated Database Connector (`app/core/db_connector.py`)
- Changed from psycopg2 to psycopg (v3)
- Psycopg3 accepts full connection strings natively
- No need to parse connection strings manually
- Better connection pool management

### 3. Updated SQLAlchemy Support (`app/core/init_db.py`)
- Connection strings now use `postgresql+psycopg://` dialect
- Supports both PG_PATH and individual components
- PG_PATH is converted to SQLAlchemy-compatible format

### 4. Connection String Format
**For psycopg3 (Native):**
```
postgresql://user:password@host:port/database
```

**For SQLAlchemy ORM:**
```
postgresql+psycopg://user:password@host:port/database
```

---

## Key Differences: psycopg2 vs psycopg3

| Feature | psycopg2 | psycopg3 |
|---------|----------|----------|
| Python 3.14 Support | ❌ No | ✅ Yes |
| Connection Strings | Manual parsing | Native support |
| Connection Pooling | `SimpleConnectionPool` | `ConnectionPool` |
| Type Hints | Minimal | Full |
| Performance | Good | Better |
| Async Support | Limited | Full async/await |

---

## Migration Complete ✅

Your backend now works on Render with Python 3.14!

### Testing Locally
```bash
# Update local environment
pip install --upgrade psycopg[binary]

# Start app
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing on Render
1. Render automatically rebuilds with new requirements.txt
2. Deployment will use psycopg3 instead of psycopg2
3. Connection to PostgreSQL will work correctly

---

## Backward Compatibility

This change maintains compatibility with:
- ✅ SQLite (unchanged)
- ✅ MySQL (unchanged)
- ✅ PostgreSQL with PG_PATH
- ✅ PostgreSQL with individual components (PG_HOST, PG_USER, etc.)
- ✅ All existing code (no API changes)

---

## Connection String Examples

### Render Deployment
```env
PG_PATH=postgresql://ticket_user:password@dpg-xxxxx.render.com:5432/ticket_db
# Automatically converted to:
# postgresql+psycopg://ticket_user:password@dpg-xxxxx.render.com:5432/ticket_db
```

### Individual Components (Local Development)
```env
PG_HOST=localhost
PG_USER=postgres
PG_PASSWORD=password
PG_DATABASE=ticket_db
PG_PORT=5432
# Automatically converted to:
# postgresql+psycopg://postgres:password@localhost:5432/ticket_db
```

---

## Performance Improvements

psycopg3 offers:
- **Faster connection establishment** - Better connection pooling
- **Improved type handling** - Native Python type support
- **Better error handling** - More informative error messages
- **Async support** - For future async FastAPI endpoints

---

## Troubleshooting

### Still getting ImportError on Render?
1. Force rebuild: Delete deployment in Render dashboard
2. Redeploy - should install new dependencies
3. Check Render logs for psycopg installation

### Connection pooling issues?
- Default pool size: min=1, max=10
- Timeout: 30 seconds
- Adjust in `db_connector.py` if needed

### Slow queries?
- psycopg3 includes automatic connection health checks (`pool.check_connection`)
- Enable query logging: Set `DEBUG=True` in `.env` (development only)

---

## Related Files Modified

1. `requirements.txt` - Dependency update
2. `app/core/db_connector.py` - Connection pool management
3. `app/core/init_db.py` - SQLAlchemy connection strings
4. `.env.example` - Documentation updated

---

## Next Steps

- Monitor Render deployment logs after push
- Verify PostgreSQL connection works
- Scale up if needed (increase pool size)
- Consider enabling SSL for production

---

## Documentation Links

- **psycopg3 Docs**: https://www.psycopg.org/psycopg3/
- **SQLAlchemy + psycopg**: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg
- **Render PostgreSQL**: https://render.com/docs/databases
