with alerts as (
    select * from {{ ref('stg_alerts') }}
),

accounts as (
    select
        account_id,
        tier,
        csm_region,
        account_status
    from {{ ref('stg_accounts') }}
),

joined as (
    select
        a.alert_id,
        a.account_id,
        a.alert_type,
        a.severity,
        a.triggered_at,
        a.acknowledged_at,
        a.resolved_at,
        a.resolved,
        a.alert_status,
        acc.tier,
        acc.csm_region,
        acc.account_status
    from alerts a
    left join accounts acc
        on a.account_id = acc.account_id
)

select * from joined
