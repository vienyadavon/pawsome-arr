import os
import pandas as pd
import duckdb
from sqlalchemy import create_engine, text

# --- CONFIGURATION ---
DUCKDB_PATH = os.path.expanduser("~/Desktop/pawsome_arr/dev.duckdb")
TARGET_SCHEMA = "marts"

# Your specific PostgreSQL Engine configuration
PG_ENGINE = create_engine(
    "postgresql://postgres:mysecretpassword@localhost:5435/pawsome_arr"
)

# List of mart tables to migrate
MART_TABLES = [
    "dim_accounts",
    "fct_mrr_by_account",
    "fct_alert_summary",
    "fct_account_health_score"
]

def migrate_marts():
    print(f"Starting migration from {DUCKDB_PATH} to PostgreSQL...")
    
    # 1. Connect to DuckDB
    try:
        duck_conn = duckdb.connect(DUCKDB_PATH, read_only=True)
    except Exception as e:
        print(f"DuckDB connection failed: {e}")
        return

    # 2. Ensure the 'marts' schema exists in PostgreSQL
    try:
        with PG_ENGINE.connect() as pg_conn:
            pg_conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TARGET_SCHEMA};"))
            pg_conn.commit()
            print(f"Schema '{TARGET_SCHEMA}' verified/created in PostgreSQL.")
    except Exception as e:
        print(f"PostgreSQL schema creation failed: {e}")
        duck_conn.close()
        return

    # 3. Loop through tables, read from DuckDB, and write to PostgreSQL
    for table in MART_TABLES:
        try:
            print(f"Processing table: {table}...")
            
            # Read table into a Pandas DataFrame
            df = duck_conn.execute(f"SELECT * FROM {table}").df()
            
            if df.empty:
                print(f"Warning: {table} is empty. Skipping.")
                continue

            # Write DataFrame to PostgreSQL 'marts' schema
            df.to_sql(
                name=table,
                con=PG_ENGINE,
                schema=TARGET_SCHEMA,
                if_exists="replace", 
                index=False,
                chunksize=10000
            )
            print(f"Successfully wrote {len(df)} rows to {TARGET_SCHEMA}.{table}")
            
        except Exception as e:
            print(f"Error migrating table {table}: {e}")
            
    # 4. Clean up connections
    duck_conn.close()
    PG_ENGINE.dispose()
    print("Migration complete!")

if __name__ == "__main__":
    migrate_marts()

