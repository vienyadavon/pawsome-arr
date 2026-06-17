with source as (
    select * from {{ source('raw', 'accounts') }}
),

renamed as (
    select
        account_id,
        company_name,
        industry,
        tier,
        arr,
        csm_region,
        cast(contract_start_date as date) as contract_start_date,
        cast(contract_end_date as date)   as contract_end_date,
        churned,
        case
            when churned = 1 then 'churned'
            else 'active'
        end as account_status
    from source
)

select * from renamed
