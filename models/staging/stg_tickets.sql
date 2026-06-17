with source as (
    select * from {{ source('raw', 'tickets') }}
),

renamed as (
    select
        ticket_id,
        account_id,
        category,
        priority,
        cast(created_at as date)  as created_at,
        cast(resolved_at as date) as resolved_at,
        satisfaction_score,
        case
            when resolved_at is null then 'open'
            else 'resolved'
        end as ticket_status
    from source
)

select * from renamed
