import csv
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd

# Define paths matching your project layout
ACCOUNTS_INPUT_PATH = "raw/accounts.csv"
ALERTS_OUTPUT_PATH = "raw/alerts.csv"


def generate_alert_data():
    # 1. Load source account data
    try:
        accounts_df = pd.read_csv(ACCOUNTS_INPUT_PATH)
    except FileNotFoundError:
        print(
            f"Error: Missing resource file. Ensure '{ACCOUNTS_INPUT_PATH}' exists before running."
        )
        return

    current_date = datetime.now().date()
    alert_records = []

    alert_types = [
        "malware_detected",
        "unauthorized_access",
        "policy_violation",
        "anomalous_behavior",
    ]
    severities = ["low", "medium", "high", "critical"]
    severity_weights = [40, 35, 20, 5]

    print("Generating account-level security alerts matrix...")

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

        # Restrict the upper limit to current system execution date if contract goes into future
        valid_end_dt = min(end_dt, current_date)
        contract_days = (valid_end_dt - start_dt).days

        # If contract just started today, handle zero-division edge case safely
        if contract_days <= 0:
            contract_days = 1

        # 3. Establish tier-based alert volume parameters
        if tier == "starter":
            num_alerts = random.randint(5, 20)
        elif tier == "growth":
            num_alerts = random.randint(20, 50)
        else:  # enterprise
            num_alerts = random.randint(50, 150)

        # 4. Generate alert timeline sequences
        for _ in range(num_alerts):
            alert_id = str(uuid.uuid4())
            alert_type = random.choice(alert_types)
            severity = random.choices(
                severities, weights=severity_weights, k=1
            )[0]

            # Trigger alert randomly inside valid contract timeline window
            random_days_offset = random.randint(0, contract_days - 1)
            triggered_dt = start_dt + timedelta(days=random_days_offset)

            # Establish acknowledgment timelines (25% null rate / risk signal)
            is_acknowledged = random.random() >= 0.25
            acknowledged_at_str = None
            resolved_at_str = None
            resolved = 0

            if is_acknowledged:
                # Acknowledged anywhere from 1 hour to 3 days after triggering
                ack_delay_days = random.randint(0, 3)
                ack_dt = triggered_dt + timedelta(days=ack_delay_days)

                # Ensure acknowledgment date doesn't exceed current run date
                if ack_dt <= current_date:
                    acknowledged_at_str = ack_dt.strftime("%Y-%m-%d")

                    # Establish resolution timelines (30% null rate / open items)
                    # Note: An item can only be resolved if it was acknowledged first
                    is_resolved = random.random() >= 0.30
                    if is_resolved:
                        # Resolved anywhere from 0 to 7 days after acknowledgment
                        res_delay_days = random.randint(0, 7)
                        res_dt = ack_dt + timedelta(days=res_delay_days)

                        if res_dt <= current_date:
                            resolved_at_str = res_dt.strftime("%Y-%m-%d")
                            resolved = 1

            alert_records.append(
                {
                    "alert_id": alert_id,
                    "account_id": account_id,
                    "alert_type": alert_type,
                    "severity": severity,
                    "triggered_at": triggered_dt.strftime("%Y-%m-%d"),
                    "acknowledged_at": acknowledged_at_str,
                    "resolved_at": resolved_at_str,
                    "resolved": resolved,
                }
            )

    # 5. Convert compiled array and export directly to CSV
    alerts_df = pd.DataFrame(alert_records)

    # Downsample slightly to align closely with your ~8,000 spec line if counts overshot
    target_rows = 8000
    if len(alerts_df) > (target_rows + 2000):
        print(
            f"Dataset organically generated {len(alerts_df)} alerts. Downsampling to stabilize near target..."
        )
        alerts_df = alerts_df.sample(n=target_rows, random_state=42)

    # Sort chronologically for clean database visualization layout
    alerts_df = alerts_df.sort_values(by="triggered_at").reset_index(drop=True)
    alerts_df.to_csv(ALERTS_OUTPUT_PATH, index=False, quoting=csv.QUOTE_MINIMAL)

    print(f"✅ Success! Security alerts data saved to: '{ALERTS_OUTPUT_PATH}'")
    print(f"Total alert records stored: {len(alerts_df)}")
    print(f"Open issues count (resolved = 0): {len(alerts_df[alerts_df['resolved'] == 0])}")
    print("\nSeverity Breakdown:")
    print(alerts_df["severity"].value_counts().to_string())
    print("\nAlert Type Breakdown:")
    print(alerts_df["alert_type"].value_counts().to_string())
    print("\nFirst 5 rows preview:")
    print(alerts_df.head())


if __name__ == "__main__":
    generate_alert_data()

