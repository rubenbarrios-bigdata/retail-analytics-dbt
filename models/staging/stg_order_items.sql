with source as (
    select * from {{ ref('raw_order_items') }}
),

renamed as (
    select
        cast(order_item_id as int64) as order_item_id,
        cast(order_id as int64) as order_id,
        cast(product_id as int64) as product_id,
        cast(quantity as int64) as quantity,
        cast(unit_price as numeric) as unit_price,
        cast(discount_amount as numeric) as discount_amount,
        round(cast(quantity as numeric) * cast(unit_price as numeric), 2) as item_gross_amount,
        round(cast(quantity as numeric) * cast(unit_price as numeric) - cast(discount_amount as numeric), 2) as item_net_amount
    from source
)

select * from renamed
