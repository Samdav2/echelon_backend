import psycopg

# Your Render database connection string
DB_URL = "postgresql://admin:plng6FWuZPZQFltCdztexTKszrODYaOc@dpg-d708ooeuk2gs7395tq20-a.oregon-postgres.render.com/echelon_9hzf"

SQL_COMMANDS = [
    """
    -- Convert the smallint column into a strict boolean
    -- It maps '1' to TRUE and anything else (like '0') to FALSE
    ALTER TABLE user_events
    ALTER COLUMN "isVerified" TYPE BOOLEAN
    USING CASE WHEN "isVerified" = 1 THEN TRUE ELSE FALSE END;
    """
]

def fix_boolean_type():
    print("⏳ Connecting to the Render database...")
    try:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                for idx, sql in enumerate(SQL_COMMANDS, 1):
                    print(f"⚙️ Applying patch {idx}/{len(SQL_COMMANDS)} for boolean conversion...")
                    cur.execute(sql)

            # Commit the transaction so the changes are saved
            conn.commit()
            print("✅ Success! 'isVerified' is now a true PostgreSQL Boolean.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    fix_boolean_type()
