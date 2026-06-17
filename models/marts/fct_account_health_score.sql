with accounts as (
    select * from {{ ref('dim_accounts') }}
),

alerts as (
    select * from {{ ref('fct_alert_summary') }}
),

tickets as (
    select
        account_id,
        count(ticket_id)                                              as total_tickets,
        sum(case when ticket_status = 'open' then 1 else 0 end)      as open_tickets,
        round(avg(satisfaction_score), 2)                            as avg_satisfaction
    from {{ ref('stg_tickets') }}
    group by account_id
),

health as (
    select
        a.account_id,
        a.company_name,
        a.tier,
        a.csm_region,
        a.account_status,
        a.arr,
        a.mrr,
        a.seat_utilization_pct,
        a.active_users,
        a.total_users,

        -- Alert signals
        coalesce(al.critical_alerts, 0)       as critical_alerts,
        coalesce(al.unacknowledged_alerts, 0) as unacknowledged_alerts,
        coalesce(al.resolution_rate_pct, 0)   as resolution_rate_pct,

        -- Ticket signals
        coalesce(t.open_tickets, 0)           as open_tickets,
        coalesce(t.avg_satisfaction, 3)       as avg_satisfaction,

        -- Health score components (each out of 100, weighted average)
        -- 1. Seat utilization (25%) — higher is better
        round(coalesce(a.seat_utilization_pct, 0), 1) as utilization_score,

        -- 2. Alert resolution rate (25%) — higher is better
        round(coalesce(al.resolution_rate_pct, 0), 1) as resolution_score,

        -- 3. User activity rate (25%) — active users / total users
        round(
            coalesce(a.active_users, 0) * 100.0
            / nullif(a.total_users, 0), 1
        ) as activity_score,

        -- 4. Satisfaction score normalized to 100 (25%)
        round(coalesce(t.avg_satisfaction, 3) * 20, 1) as satisfaction_score,

        -- Composite health score
        round((
            round(coalesce(a.seat_utilization_pct, 0), 1) +
            round(coalesce(al.resolution_rate_pct, 0), 1) +
            round(coalesce(a.active_users, 0) * 100.0 / nullif(a.total_users, 0), 1) +
            round(coalesce(t.avg_satisfaction, 3) * 20, 1)
        ) / 4, 1) as health_score

    from accounts a
    left join alerts al on a.account_id = al.account_id
    left join tickets t on a.account_id = t.account_id
)

select * from health
order by health_score asc
