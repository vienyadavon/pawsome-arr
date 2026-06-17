with source as (
    select * from {{ source('raw', 'alerts') }}
),

renamed as (
    select
        alert_id,
        account_id,
        alert_type,
        severity,
        cast(triggered_at as date)    as triggered_at,
        cast(acknowledged_at as date) as acknowledged_at,
        cast(resolved_at as date)     as resolved_at,
        resolved,
        case
            when resolved = 1 then 'resolved'
            when acknowledged_at is not null then 'acknowledged'
            else 'unacknowledged'
        end as alert_status
    from source
)

select * from renamed
