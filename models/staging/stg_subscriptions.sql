with source as (
    select * from {{ source('raw', 'subscriptions') }}
),

renamed as (
    select
        subscription_id,
        account_id,
        plan_name,
        seats_purchased,
        seats_used,
        mrr,
        cast(start_date as date) as start_date,
        cast(end_date as date)   as end_date,
        status,
        round(seats_used * 100.0 / nullif(seats_purchased, 0), 1) as seat_utilization_pct
    from source
)

select * from renamed
