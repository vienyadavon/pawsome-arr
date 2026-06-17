import csv
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd

# Define paths matching your project layout
ACCOUNTS_INPUT_PATH = "raw/accounts.csv"
TICKETS_OUTPUT_PATH = "raw/tickets.csv"


def generate_ticket_data():
    # 1. Load source account data
    try:
        accounts_df = pd.read_csv(ACCOUNTS_INPUT_PATH)
    except FileNotFoundError:
        print(
            f"Error: Missing resource file. Ensure '{ACCOUNTS_INPUT_PATH}' exists before running."
        )
        return

    current_date = datetime.now().date()
    ticket_records = []

    categories = ["billing", "technical", "onboarding", "feature_request"]
    priorities = ["low", "medium", "high"]
    priority_weights = [50, 35, 15]

    print("Generating account-level customer support tickets matrix...")

    # 2. Process every account record to apply tier volumes
    for idx, account in accounts_df.iterrows():
        account_id = account["account_id"]
        tier = account["tier"]

        # Parse contract timeline dates safely
        start_dt = datetime.strptime(
            account["contract_start_date"], "%Y-%m-%d"
        ).date()
        end_dt = datetime.strptime(
            account["contract_end_date"], "%Y-%m-%d"
        ).date()

        # Restrict upper limit to current system execution date if contract goes into the future
        valid_end_dt = min(end_dt, current_date)
        contract_days = (valid_end_dt - start_dt).days

        # Safe guard for zero-division edge case if contract started today
        if contract_days <= 0:
            contract_days = 1

        # 3. Establish tier-based ticket volume parameters
        if tier == "starter":
            num_tickets = random.randint(1, 5)
        elif tier == "growth":
            num_tickets = random.randint(3, 10)
        else:  # enterprise
            num_tickets = random.randint(8, 25)

        # 4. Generate specific ticket rows
        for _ in range(num_tickets):
            ticket_id = str(uuid.uuid4())
            category = random.choice(categories)
            priority = random.choices(
                priorities, weights=priority_weights, k=1
            )[0]

            # Generate creation date randomly inside valid contract timeline window
            random_days_offset = random.randint(0, contract_days - 1)
            created_dt = start_dt + timedelta(days=random_days_offset)

            # Establish resolution timelines (20% null rate / open tickets)
            is_resolved = random.random() >= 0.20
            resolved_at_str = None
            satisfaction_score = None

            if is_resolved:
                # Resolved anywhere from 0 to 14 days after creation
                res_delay_days = random.randint(0, 14)
                res_dt = created_dt + timedelta(days=res_delay_days)

                # Ensure resolution date doesn't exceed current run date
                if res_dt <= current_date:
                    resolved_at_str = res_dt.strftime("%Y-%m-%d")

                    # Satisfaction score — only if resolved, and null for ~30% of those
                    is_rated = random.random() >= 0.30
                    if is_rated:
                        satisfaction_score = random.randint(1, 5)

            ticket_records.append(
                {
                    "ticket_id": ticket_id,
                    "account_id": account_id,
                    "category": category,
                    "priority": priority,
                    "created_at": created_dt.strftime("%Y-%m-%d"),
                    "resolved_at": resolved_at_str,
                    "satisfaction_score": satisfaction_score,
                }
            )

    # 5. Convert compiled array and export directly to CSV
    tickets_df = pd.DataFrame(ticket_records)

    # Downsample slightly to align closely with your ~1,200 row spec if counts overshot
    target_rows = 1200
    if len(tickets_df) > (target_rows + 300):
        print(
            f"Dataset organically generated {len(tickets_df)} tickets. Downsampling to stabilize near target..."
        )
        tickets_df = tickets_df.sample(n=target_rows, random_state=42)

    # Sort chronologically for clean database visualization layout
    tickets_df = tickets_df.sort_values(by="created_at").reset_index(drop=True)
    tickets_df.to_csv(
        TICKETS_OUTPUT_PATH, index=False, quoting=csv.QUOTE_MINIMAL
    )

    print(f"✅ Success! Support tickets data saved to: '{TICKETS_OUTPUT_PATH}'")
    print(f"Total ticket records stored: {len(tickets_df)}")
    print(f"Open tickets count (resolved_at is null): {tickets_df['resolved_at'].isna().sum()}")
    print(f"Unrated tickets count (score is null): {tickets_df['satisfaction_score'].isna().sum()}")
    print("\nCategory Distribution:")
    print(tickets_df["category"].value_counts().to_string())
    print("\nPriority Breakdown:")
    print(tickets_df["priority"].value_counts().to_string())
    print("\nFirst 5 rows preview:")
    print(tickets_df.head())


if __name__ == "__main__":
    generate_ticket_data()
    #generate_event_data() 
    #if "generate_event_data" in locals() else generate_ticket_data()

