with source as (
    select * from {{ ref('raw_products') }}
),

renamed as (
    select
        cast(product_id as int64) as product_id,
        trim(product_name) as product_name,
        trim(category) as category,
        cast(cost_price as numeric) as cost_price,
        cast(list_price as numeric) as list_price,
        round(cast(list_price as numeric) - cast(cost_price as numeric), 2) as unit_margin,
        round(safe_divide(cast(list_price as numeric) - cast(cost_price as numeric), cast(list_price as numeric)) * 100, 2) as margin_percentage
    from source
)

select * from renamed
