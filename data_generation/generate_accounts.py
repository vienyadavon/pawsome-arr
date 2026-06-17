import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd

# Initialize Faker
fake = Faker()

def generate_account_data(num_records=500):
    # Establish dynamic parameters (4 spaces)
    industries = ["Healthcare", "Finance", "Retail", "Manufacturing", "Technology"]
    tiers = ["starter", "growth", "enterprise"]
    regions = ["NA", "EMEA", "APAC"]
    current_date = datetime.now().date()
    records = []

    for _ in range(num_records):
        # All loop content must be exactly 8 spaces
        account_id = str(uuid.uuid4())
        company_name = fake.company()
        industry = random.choice(industries)
        tier = random.choice(tiers)
        csm_region = random.choice(regions)

        if tier == "starter":
            arr = random.randint(5000, 15000)
        elif tier == "growth":
            arr = random.randint(15000, 80000)
        else:
            arr = random.randint(80000, 300000)

        # Spread start dates across 2023, 2024, and 2025
        start_year = random.choices([2023, 2024, 2025], weights=[20,40,40])[0]
        start_month = random.randint(1, 12)
        start_day = random.randint(1, 28)
        contract_start_date = datetime(start_year, start_month, start_day).date()

        duration_months = random.choice([12, 24])
        days_to_add = int(duration_months * 30.4375)
        contract_end_date = contract_start_date + timedelta(days=days_to_add)

        churned = 1 if contract_end_date < current_date else 0

        records.append({
            "account_id": account_id,
            "company_name": company_name,
            "industry": industry,
            "tier": tier,
            "arr": arr,
            "csm_region": csm_region,
            "contract_start_date": contract_start_date,
            "contract_end_date": contract_end_date,
            "churned": churned
        })

    # This sits precisely at 4 spaces, marking it inside the function
    return pd.DataFrame(records)

# Execution blocks (0 spaces - flush against the left margin)
account_df = generate_account_data(num_records=500)
account_df["account_id"].to_csv("raw/account_ids.csv", index=False)
output_file = "raw/accounts.csv"
account_df.to_csv(output_file, index=False)
print(f"Success! Generated spreadsheet saved to: '{output_file}'")
print(account_df.head())

