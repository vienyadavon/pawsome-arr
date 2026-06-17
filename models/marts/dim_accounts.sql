with base as (
    select * from {{ ref('int_accounts_enriched') }}
)

select
    account_id,
    company_name,
    industry,
    tier,
    arr,
    mrr,
    csm_region,
    plan_name,
    seats_purchased,
    seats_used,
    seat_utilization_pct,
    total_users,
    active_users,
    shelfware_users,
    contract_start_date,
    contract_end_date,
    account_status
from base
