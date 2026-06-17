import csv
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd

# Define paths matching your project layout
ACCOUNTS_INPUT_PATH = "raw/accounts.csv"
USERS_INPUT_PATH = "raw/users.csv"
EVENTS_OUTPUT_PATH = "raw/events.csv"


def generate_event_data():
    # 1. Load source data
    try:
        accounts_df = pd.read_csv(ACCOUNTS_INPUT_PATH)
        users_df = pd.read_csv(USERS_INPUT_PATH)
    except FileNotFoundError as e:
        print(
            f"Error: Missing resource file. Ensure raw/accounts.csv and raw/users.csv exist. Details: {e}"
        )
        return

    # 2. Merge users and accounts so every user contains tier, contract, and churn data
    merged_df = pd.merge(
        users_df,
        accounts_df,
        on="account_id",
        how="inner",
        suffixes=("_user", "_acct"),
    )

    current_date = datetime.now().date()
    event_records = []

    event_types = [
        "login",
        "scan_started",
        "alert_viewed",
        "report_exported",
        "setting_changed",
    ]
    event_weights = [40, 25, 20, 10, 5]

    print("Processing user history matrix to compile telemetry...")

    # 3. Process every user line item sequentially
    for idx, user in merged_df.iterrows():
        # Parse dates safely from the dataset
        user_created_dt = datetime.strptime(
            user["created_at"], "%Y-%m-%d"
        ).date()
        contract_end_dt = datetime.strptime(
            user["contract_end_date"], "%Y-%m-%d"
        ).date()

        tier = user["tier"]
        churned_acct = user["churned"]
        account_id = user["account_id"]
        user_id = user["user_id"]

        # Calculate a realistic dropoff point for churned entities
        dropoff_start_dt = None
        if churned_acct == 1:
            dropoff_start_dt = contract_end_dt - timedelta(
                days=random.randint(60, 90)
            )

        # Apply your updated window constraints
        window_start = max(user_created_dt, current_date - timedelta(days=365))
        window_end = min(contract_end_dt, current_date)
        current_loop_dt = window_start

        # 4. Generate daily event chronological loop bounded by window_end
        while current_loop_dt <= window_end:

            # Apply Churn Dropoff Logic check
            in_dropoff_zone = (
                dropoff_start_dt is not None
                and current_loop_dt >= dropoff_start_dt
            )
            if in_dropoff_zone and random.random() > 0.20:
                # 80% chance to entirely skip generating events for this day during a churn dropoff
                current_loop_dt += timedelta(days=1)
                continue

            # Apply Tier-based Volume constraints
            if tier == "starter":
                daily_events_count = random.randint(1, 3)
            elif tier == "growth":
                daily_events_count = random.randint(2, 6)
            else:  # enterprise
                daily_events_count = random.randint(4, 12)

            # Reduce volume further inside the dropoff zone if any events survived the skip check
            if in_dropoff_zone:
                daily_events_count = max(
                    1, int(daily_events_count * 0.5)
                )  # Halve remaining event count

            # Randomize daily user pacing (simulate standard weekends/days off)
            skip_probability = 0.4 if user["role"] == "viewer" else 0.15
            if random.random() < skip_probability and not in_dropoff_zone:
                current_loop_dt += timedelta(days=1)
                continue

            # Session grouping — unique session token minted once per user, per active day
            session_id = str(uuid.uuid4())
            loop_date_str = current_loop_dt.strftime("%Y-%m-%d")

            # 5. Populate specific daily events
            for _ in range(daily_events_count):
                chosen_event = random.choices(
                    event_types, weights=event_weights, k=1
                )[0]

                event_records.append(
                    {
                        "event_id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "account_id": account_id,
                        "event_type": chosen_event,
                        "occurred_at": loop_date_str,
                        "session_id": session_id,
                    }
                )

            current_loop_dt += timedelta(days=1)

    # 6. Guard and optimize DataFrame formatting
    events_df = pd.DataFrame(event_records)
    target_rows = 150000

    if len(events_df) == 0:
        print(
            "🔴 Critical Error: 0 events generated. Check if your user creation dates or contract windows overlap with the rolling 12-month period."
        )
        return

    if len(events_df) > (target_rows + 20000):
        print(
            f"Dataset organically generated {len(events_df)} rows. Downsampling to stabilize around {target_rows}..."
        )
        events_df = events_df.sample(n=target_rows, random_state=42)

    # Sort chronologically for clean analytical ingestion layout
    events_df = events_df.sort_values(by="occurred_at").reset_index(drop=True)

    # Export directly to targeted raw path
    events_df.to_csv(EVENTS_OUTPUT_PATH, index=False, quoting=csv.QUOTE_MINIMAL)

    print(f"✅ Success! Telemetry data generated at: '{EVENTS_OUTPUT_PATH}'")
    print(f"Total event rows stored: {len(events_df)}")
    print("\nEvent Distribution:")
    print(events_df["event_type"].value_counts().to_string())
    print(f"Raw events generated before downsampling: {len(events_df)}")


if __name__ == "__main__":
    generate_event_data()

