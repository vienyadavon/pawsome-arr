with accounts as (
    select * from {{ ref('stg_accounts') }}
),

subscriptions as (
    select * from {{ ref('stg_subscriptions') }}
),

users as (
    select * from {{ ref('stg_users') }}
),

user_summary as (
    select
        account_id,
        count(user_id)                                    as total_users,
        sum(case when user_status = 'active' then 1 else 0 end)       as active_users,
        sum(case when user_status = 'never_logged_in' then 1 else 0 end) as shelfware_users
    from users
    group by account_id
),

joined as (
    select
        a.account_id,
        a.company_name,
        a.industry,
        a.tier,
        a.arr,
        a.csm_region,
        a.contract_start_date,
        a.contract_end_date,
        a.account_status,
        s.plan_name,
        s.seats_purchased,
        s.seats_used,
        s.seat_utilization_pct,
        s.mrr,
        u.total_users,
        u.active_users,
        u.shelfware_users
    from accounts a
    left join subscriptions s
        on a.account_id = s.account_id
        and s.status in ('active', 'renewed')
    left join user_summary u
        on a.account_id = u.account_id
)

select * from joined
