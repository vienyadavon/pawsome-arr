# Pawsome ARR — SaaS Revenue & Customer Health Analytics

A dbt + DuckDB analytics project built on simulated SaaS data for the 
fictional ARR team at Pawsome Provisions — a pet food manufacturing company.

This project represents Layer 4 of the Pawsome Provisions portfolio, adding 
a professional data transformation layer on top of an existing BI stack. 
While the domain is fictional, the data model, metrics, and tooling reflect 
real-world CS and RevOps workflows.

---

## What This Project Demonstrates

- **dbt** — staging, intermediate, and mart models with tests and documentation
- **DuckDB** — lightweight analytical database, no infrastructure required
- **Python** — simulated data generation across six source tables
- **PostgreSQL + Docker** — serving layer for BI consumption
- **Metabase** — CS and RevOps dashboards built on dbt mart models

---

## The Data Story

The Pawsome Provisions ARR team tracks three things:

1. **Customer health** — are accounts engaged, resolving alerts, and satisfied?
2. **Revenue** — where is MRR coming from and where is it at risk?
3. **Alert operations** — are security alerts being acknowledged and resolved?

These questions map directly to the CS Engineer and RevOps Analyst roles 
this project is designed to speak to.

---

## Project Structure
pawsome_arr/

│

├── data_generation/          # Python scripts to simulate raw source data

│   ├── generate_accounts.py

│   ├── generate_users.py

│   ├── generate_subscriptions.py

│   ├── generate_events.py

│   ├── generate_alerts.py

│   ├── generate_tickets.py

│   ├── load_to_duckdb.py     # Loads CSVs into DuckDB raw schema

│   └── raw/                  # Generated CSVs (6 source tables)

│

├── models/

│   ├── staging/              # Cleaned and renamed source tables (views)

│   ├── intermediate/         # Joined and enriched models (views)

│   └── marts/                # CS/RevOps reporting tables (tables)

│

├── bi/

│   ├── docker-compose.yml    # PostgreSQL + Metabase containers

│   └── load_marts_to_postgres.py  # Migrates dbt marts to PostgreSQL

│

└── dbt_project.yml

---

## Data Model

### Sources (raw schema in DuckDB)
Six simulated source tables loaded via Python and DuckDB:

| Table | Rows | Description |
|---|---|---|
| `accounts` | 500 | Customer organisations — tier, ARR, contract dates |
| `users` | ~3,700 | Users per account — role, login activity |
| `subscriptions` | 533 | Plan, seats, MRR, renewal history |
| `events` | 150,000 | Product telemetry — logins, scans, exports |
| `alerts` | 8,000 | Security alerts — severity, acknowledgment, resolution |
| `tickets` | 1,200 | Support tickets — category, priority, satisfaction |

### dbt Layers

**Staging** — cleans and renames raw sources, adds derived status fields  
**Intermediate** — joins accounts with subscriptions and users, enriches alerts with account context  
**Marts** — four reporting tables built for CS and RevOps consumption:

| Mart | Description |
|---|---|
| `dim_accounts` | Enriched account dimension |
| `fct_mrr_by_account` | MRR with tier and region context |
| `fct_alert_summary` | Alert volume, severity, and resolution by account |
| `fct_account_health_score` | Composite health score — utilization, alerts, activity, satisfaction |

---

## dbt Project Stats

- **12 models** — 6 staging, 2 intermediate, 4 marts
- **34 tests** — unique, not_null, accepted_values across all layers
- **6 sources** declared with column-level documentation
- Full lineage DAG auto-generated via `dbt docs generate`

---

## Account Health Score

The composite health score (0-100) is the centrepiece of this project. 
It combines four equally weighted signals:

| Signal | Source | Weight |
|---|---|---|
| Seat utilization | subscriptions | 25% |
| Alert resolution rate | alerts | 25% |
| User activity rate | users | 25% |
| Satisfaction score (normalized) | tickets | 25% |

Accounts scoring below 50 are flagged as churn risk in the dashboard.

---

## Running Locally

### Prerequisites
- Python 3.10+
- dbt-duckdb (`pip install dbt-duckdb`)
- Docker and Docker Compose

### Steps

```bash
# 1. Generate simulated data
cd data_generation
python3 generate_accounts.py
python3 generate_users.py
python3 generate_subscriptions.py
python3 generate_events.py
python3 generate_alerts.py
python3 generate_tickets.py

# 2. Load CSVs into DuckDB
python3 load_to_duckdb.py

# 3. Run dbt
cd ..
dbt run
dbt test

# 4. Start BI environment
cd bi
docker compose up -d
python3 load_marts_to_postgres.py

# 5. Open Metabase
# http://localhost:3001
```

---

## Metabase Dashboards

Three dashboards built on dbt mart models:

- **Account Health Overview** — health score distribution, churn risk list, ARR vs health scatter
- **MRR & Revenue** — total MRR, breakdown by tier and region, active vs churned ARR
- **Alert Operations** — unacknowledged alerts, resolution rate by tier, critical alerts by account

Dashboard screenshots available at: https://portfolio2026.z19.web.core.windows.net/dbt.html

---

## Part of a Larger Project

This repo is Layer 4 of the Pawsome Provisions portfolio — a multi-layer 
data engineering project spanning IoT simulation, inventory management, 
SQL analytics, and now dbt transformations.

🔗 https://github.com/vienyadavon/pawsome-provisions
🔗 https://portfolio2026.z19.web.core.windows.net/index.html

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3 | Data simulation and loading |
| DuckDB | Analytical database |
| dbt-duckdb | Data transformation layer |
| PostgreSQL | BI serving layer |
| Docker | Containerised environment |
| Metabase | Self-hosted dashboards |

---

*All data, characters, and business scenarios are entirely fictional 
and created for portfolio demonstration purposes only.*

---

## Development Notes

This project was built with AI assistance from two tools:

**Claude (Anthropic)** was used for architecture guidance, dbt project 
structure, code review, and pair programming throughout the transformation 
layer — staging models, intermediate models, marts, tests, and documentation. 
All design decisions, domain framing, debugging, and implementation are my own work.

**Google Gemini** was used to assist with the six simulated data generation 
scripts (generate_accounts.py through generate_tickets.py). Generating 
realistic randomised business data across multiple related tables required 
domain knowledge I leaned on AI to bridge — RevOps and SaaS metrics aren't 
my native language. The resulting scripts were reviewed, troubleshot, tested, 
and integrated by me.

Both tools were used as collaborative assistants, not replacements for 
engineering judgment.
