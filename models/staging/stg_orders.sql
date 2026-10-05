with source as (
    select * from {{ ref('raw_orders') }}
),

renamed as (
    select
        cast(order_id as int64) as order_id,
        cast(customer_id as int64) as customer_id,
        cast(order_date as date) as order_date,
        lower(trim(status)) as status,
        lower(trim(channel)) as channel
    from source
)

select * from renamed
