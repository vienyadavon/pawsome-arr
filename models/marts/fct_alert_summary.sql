with alerts as (
    select * from {{ ref('int_alerts_enriched') }}
)

select
    account_id,
    tier,
    csm_region,
    account_status,
    count(alert_id)                                                    as total_alerts,
    sum(case when severity = 'critical' then 1 else 0 end)            as critical_alerts,
    sum(case when severity = 'high' then 1 else 0 end)                as high_alerts,
    sum(case when alert_status = 'unacknowledged' then 1 else 0 end)  as unacknowledged_alerts,
    sum(case when resolved = 1 then 1 else 0 end)                     as resolved_alerts,
    round(
        sum(case when resolved = 1 then 1 else 0 end) * 100.0
        / nullif(count(alert_id), 0), 1
    )                                                                  as resolution_rate_pct
from alerts
group by account_id, tier, csm_region, account_status
order by critical_alerts desc
