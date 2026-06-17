import os
import duckdb
import pandas as pd

# 1. Define dev.duckdb path (Expanding '~' to handle the home directory safely)
DB_PATH = os.path.expanduser("~/Desktop/pawsome_arr/dev.duckdb")

# Dictionary holding explicit column type configurations
COLUMN_TYPES = {
    "accounts": {
        "dates": ["contract_start_date", "contract_end_date"],
        "dtypes": {"churned": "Int64"},  # Uses Pandas nullable integer
    },
    "users": {
        "dates": ["created_at", "last_login_at"],
        "dtypes": {"is_active": "Int64"},
    },
    "subscriptions": {"dates": ["start_date", "end_date"], "dtypes": {}},
    "events": {"dates": ["occurred_at"], "dtypes": {}},
    "alerts": {
        "dates": ["triggered_at", "acknowledged_at", "resolved_at"],
        "dtypes": {"resolved": "Int64"},
    },
    "tickets": {
        "dates": ["created_at", "resolved_at"],
        "dtypes": {"satisfaction_score": "Int64"},
    },
}

# 2. File to table mapping
tables = {
    "accounts": "raw/accounts.csv",
    "users": "raw/users.csv",
    "subscriptions": "raw/subscriptions.csv",
    "events": "raw/events.csv",
    "alerts": "raw/alerts.csv",
    "tickets": "raw/tickets.csv",
}


def main():
    # Ensure directory path for the database exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # 3. Connect to duckdb
    conn = duckdb.connect(DB_PATH)

    try:
        # 4. CREATE SCHEMA IF NOT EXISTS raw
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        print("Schema 'raw' verified/created.\n" + "=" * 40)

        # 5. For each CSV
        for table_name, csv_path in tables.items():
            if not os.path.exists(csv_path):
                print(f"Error: File not found at {csv_path}. Skipping.")
                continue

            # Fetch specific configuration mapping for this table
            config = COLUMN_TYPES.get(table_name, {"dates": [], "dtypes": {}})

            # Read into pandas with explicit dtypes
            # 'parse_dates' converts columns to datetime64[ns]
            # 'dtype' enforces types on fields (e.g. nullable integers to preserve blanks safely)
            df = pd.read_csv(
                csv_path, parse_dates=config["dates"], dtype=config["dtypes"]
            )

            # Write to duckdb as raw.table_name
            # 'CREATE OR REPLACE TABLE' handles script re-runs cleanly
            conn.execute(
                f"CREATE OR REPLACE TABLE raw.{table_name} AS SELECT * FROM df"
            )

            # 6. Print confirmation + row counts
            row_count = conn.execute(
                f"SELECT COUNT(*) FROM raw.{table_name}"
            ).fetchone()[0]
            print(
                f"Successfully loaded {csv_path} -> raw.{table_name} ({row_count} rows)"
            )

        print("=" * 40 + "\nAll specified tables loaded successfully!")

    except Exception as e:
        print(f"\nAn error occurred during execution: {e}")

    finally:
        # Close connection to flush data safely to disk
        conn.close()


if __name__ == "__main__":
    main()

