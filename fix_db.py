import sys
import logging
from app.core.init_db import DatabaseInitializer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_db_fix():
    logger.info("⏳ Initializing database and running schema synchronization...")
    success = DatabaseInitializer.initialize_database()
    if success:
        logger.info("✅ Database schema sync completed successfully!")
    else:
        logger.error("❌ Database schema sync failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_db_fix()

