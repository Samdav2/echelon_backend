import psycopg

# Your Render database connection string
DB_URL = "postgresql://admin:plng6FWuZPZQFltCdztexTKszrODYaOc@dpg-d708ooeuk2gs7395tq20-a.oregon-postgres.render.com/echelon_9hzf"

SQL_COMMANDS = [
    """
    -- Add the primary key 'id' column, auto-incrementing
    ALTER TABLE user_interests
    ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY;
    """,
    """
    -- Add the missing timestamp columns
    ALTER TABLE user_interests
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    """
]

def fix_user_interests():
    print("⏳ Connecting to the Render database...")
    try:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                for idx, sql in enumerate(SQL_COMMANDS, 1):
                    print(f"⚙️ Applying patch {idx}/{len(SQL_COMMANDS)} for user_interests...")
                    cur.execute(sql)

            # Commit the transaction so the changes are saved
            conn.commit()
            print("✅ Success! The 'user_interests' table now has an 'id' column and timestamps.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    fix_user_interests()
