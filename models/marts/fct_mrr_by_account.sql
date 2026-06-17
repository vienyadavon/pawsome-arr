with accounts as (
    select * from {{ ref('dim_accounts') }}
)

select
    account_id,
    company_name,
    tier,
    csm_region,
    industry,
    arr,
    mrr,
    account_status,
    contract_start_date,
    contract_end_date
from accounts
order by mrr desc
