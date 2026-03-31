import psycopg

# Your Render database connection string
DB_URL = "postgresql://admin:plng6FWuZPZQFltCdztexTKszrODYaOc@dpg-d708ooeuk2gs7395tq20-a.oregon-postgres.render.com/echelon_9hzf"

SQL_COMMANDS = [
    """
    -- Rename the lowercase column to the case-sensitive camelCase name
    ALTER TABLE user_events RENAME COLUMN isverified TO "isVerified";
    """
]

def fix_user_events_case():
    print("⏳ Connecting to the Render database...")
    try:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                for idx, sql in enumerate(SQL_COMMANDS, 1):
                    print(f"⚙️ Applying patch {idx}/{len(SQL_COMMANDS)} for user_events...")
                    cur.execute(sql)

            # Commit the transaction so the changes are saved
            conn.commit()
            print("✅ Success! 'isverified' is now strictly named 'isVerified'.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    fix_user_events_case()
