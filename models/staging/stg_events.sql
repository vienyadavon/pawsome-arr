with source as (
    select * from {{ source('raw', 'events') }}
),

renamed as (
    select
        event_id,
        user_id,
        account_id,
        event_type,
        cast(occurred_at as date) as occurred_at,
        session_id
    from source
)

select * from renamed
