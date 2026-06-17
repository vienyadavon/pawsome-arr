with source as (
    select * from {{ source('raw', 'users') }}
),

renamed as (
    select
        user_id,
        account_id,
        role,
        cast(created_at as date)      as created_at,
        cast(last_login_at as date)   as last_login_at,
        is_active,
        case
            when last_login_at is null then 'never_logged_in'
            when is_active = 0 then 'inactive'
            else 'active'
        end as user_status
    from source
)

select * from renamed
