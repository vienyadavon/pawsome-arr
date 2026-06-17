import csv
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd

# Define path configurations
ACCOUNTS_INPUT_PATH = "raw/accounts.csv"
SUBSCRIPTIONS_OUTPUT_PATH = "raw/subscriptions.csv"


def generate_subscription_data():
    # 1. Safely load the accounts.csv dataset
    try:
        accounts_df = pd.read_csv(ACCOUNTS_INPUT_PATH)
    except FileNotFoundError:
        print(
            f"Error: Could not find account file at '{ACCOUNTS_INPUT_PATH}'. Please ensure it is in this folder."
        )
        return

    current_date = datetime.now().date()
    subscription_records = []

    # 2. Process each account row from accounts.csv
    for _, account in accounts_df.iterrows():
        account_id = account["account_id"]
        tier = account["tier"]
        arr = account["arr"]
        churned_flag = account["churned"]

        # Parse contract timeline dates cleanly
        start_str = account["contract_start_date"]
        end_str = account["contract_end_date"]
        start_dt = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_str, "%Y-%m-%d").date()

        # 3. Determine seating bands based on core tier constraints
        if tier == "starter":
            seats_purchased = random.randint(5, 20)
        elif tier == "growth":
            seats_purchased = random.randint(20, 100)
        else:  # enterprise
            seats_purchased = random.randint(100, 500)

        seats_used = random.randint(int(seats_purchased * 0.5), seats_purchased)
        mrr = round(arr / 12)

        # 4. Handle Status Rules and Renewal History Logic
        # Default active/churned assignment
        if churned_flag == 1:
            status = "churned"
            is_renewed_account = False
        else:
            # Check if this active account will be given a renewal history sequence (20% chance)
            is_renewed_account = random.random() < 0.20
            status = "renewed" if is_renewed_account else "active"

        # 5. Build the primary current/historical record row
        subscription_records.append(
            {
                "subscription_id": str(uuid.uuid4()),
                "account_id": account_id,
                "plan_name": tier,
                "seats_purchased": seats_purchased,
                "seats_used": seats_used,
                "mrr": mrr,
                "start_date": start_str,
                "end_date": end_str,
                "status": status,
            }
        )

        # 6. For the ~20% marked renewed, inject a historic transaction block
        if is_renewed_account:
            # The prior cycle ended exactly when the current one started
            prior_end_dt = start_dt
            # Approximate a 12-month historical window
            prior_start_dt = prior_end_dt - timedelta(days=365)

            # Generate historical seating parameters (often slightly lower than current)
            prior_seats_purchased = max(5, int(seats_purchased * 0.8))
            prior_seats_used = random.randint(
                int(prior_seats_purchased * 0.5), prior_seats_purchased
            )
            prior_mrr = max(1, int(mrr * 0.8))

            subscription_records.append(
                {
                    "subscription_id": str(uuid.uuid4()),
                    "account_id": account_id,
                    "plan_name": tier,
                    "seats_purchased": prior_seats_purchased,
                    "seats_used": prior_seats_used,
                    "mrr": prior_mrr,
                    "start_date": prior_start_dt.strftime("%Y-%m-%d"),
                    "end_date": prior_end_dt.strftime("%Y-%m-%d"),
                    "status": "renewed",  # Marked historical status flag
                }
            )

    # 7. Convert compiled array and export directly to clean formatted CSV
    subscriptions_df = pd.DataFrame(subscription_records)

    # Optional: Shuffle rows so the historical entries are mixed organically rather than paired sequentially
    subscriptions_df = subscriptions_df.sample(frac=1).reset_index(drop=True)

    subscriptions_df.to_csv(
        SUBSCRIPTIONS_OUTPUT_PATH, index=False, quoting=csv.QUOTE_MINIMAL
    )

    print(
        f"✅ Success! Subscriptions file generated at: '{SUBSCRIPTIONS_OUTPUT_PATH}'"
    )
    print(f"Total subscription line items: {len(subscriptions_df)}")
    print(subscriptions_df["status"].value_counts().to_string())


if __name__ == "__main__":
    generate_subscription_data()


