import csv
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd

# Define paths matching your project layout
ACCOUNTS_INPUT_PATH = (
    "raw/accounts.csv"
)
USERS_OUTPUT_PATH = (
    "raw/users.csv"
)


def generate_user_data():
    # 1. Load the existing accounts file to capture FKs and contract dates
    try:
        accounts_df = pd.read_csv(ACCOUNTS_INPUT_PATH)
    except FileNotFoundError:
        print(
            f"Error: Could not find account file at {ACCOUNTS_INPUT_PATH}. Please run the account generation script first."
        )
        return

    # Establish dynamic reference dates based on current run time
    current_date = datetime.now().date()

    roles = ["admin", "analyst", "viewer"]
    user_records = []

    # 2. Iterate through each account and assign a variable number of users
    for _, account in accounts_df.iterrows():
        account_id = account["account_id"]

        # Safely extract and parse the contract start date
        contract_start = account["contract_start_date"]
        if isinstance(contract_start, str):
            contract_start_dt = datetime.strptime(
                contract_start, "%Y-%m-%d"
            ).date()
        elif hasattr(contract_start, "date"):
            contract_start_dt = contract_start.date()
        else:
            contract_start_dt = contract_start

        # Assign 5-10 users randomly per account to reach ~1,500 rows across 500 accounts
        num_users_for_account = random.randint(5, 10)

        for _ in range(num_users_for_account):
            user_id = str(uuid.uuid4())
            role = random.choice(roles)

            # 3. Handle created_at (On or after the account's contract start date)
            days_since_contract = (current_date - contract_start_dt).days
            if days_since_contract <= 0:
                # If contract started today or in the future, create user on start date
                created_at_dt = contract_start_dt
            else:
                # Randomize creation day between contract start and today
                random_days_to_add = random.randint(0, days_since_contract)
                created_at_dt = contract_start_dt + timedelta(
                    days=random_days_to_add
                )

            # 4. Handle last_login_at logic (15% shelfware signal / Nullable)
            is_shelfware = random.random() < 0.15

            if is_shelfware:
                last_login_at = None
            else:
                # User has logged in. Randomize a login date between creation and today
                days_since_creation = (current_date - created_at_dt).days
                if days_since_creation <= 0:
                    last_login_at_dt = created_at_dt
                else:
                    random_login_offset = random.randint(0, days_since_creation)
                    last_login_at_dt = created_at_dt + timedelta(
                        days=random_login_offset
                    )
                last_login_at = last_login_at_dt.strftime("%Y-%m-%d")

            # 5. Handle is_active logic based on inactivity metrics
            # Condition: inactive if never logged in OR last login was 90+ days ago
            if last_login_at is None:
                is_active = 0
            else:
                days_inactive = (current_date - last_login_at_dt).days
                if days_inactive >= 180:
                    is_active = 0
                else:
                    # Active user (logged in within the last 90 days)
                    is_active = 1

            # Format dates to clean ISO strings for CSV storage
            created_at_str = created_at_dt.strftime("%Y-%m-%d")

            user_records.append(
                {
                    "user_id": user_id,
                    "account_id": account_id,
                    "role": role,
                    "created_at": created_at_str,
                    "last_login_at": last_login_at,
                    "is_active": is_active,
                }
            )

    # 6. Export directly to a clean CSV
    users_df = pd.DataFrame(user_records)
    users_df.to_csv(USERS_OUTPUT_PATH, index=False, quoting=csv.QUOTE_MINIMAL)

    print(f"✅ Success! Generated user dataset saved to: '{USERS_OUTPUT_PATH}'")
    print(f"Total user rows generated: {len(users_df)}")
    print(
        f"Inactive users flag count (shelfware + inactive): {len(users_df[users_df['is_active'] == 0])}"
    )
    print("\nFirst 5 rows preview:  ")
    print(users_df.head())


if __name__ == "__main__":
    generate_user_data()

