with orders as (
    select * from {{ ref('stg_orders') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

order_items_aggregated as (
    select
        order_id,
        count(order_item_id) as total_items_count,
        sum(quantity) as total_units_count,
        round(sum(item_gross_amount), 2) as gross_amount,
        round(sum(discount_amount), 2) as total_discount_amount,
        round(sum(item_net_amount), 2) as net_amount
    from order_items
    group by order_id
),

final as (
    select
        o.order_id,
        o.customer_id,
        o.order_date,
        extract(year from o.order_date) as order_year,
        extract(month from o.order_date) as order_month,
        format_date('%Y-%m', o.order_date) as order_year_month,
        o.status,
        o.channel,
        coalesce(oia.total_items_count, 0) as total_items_count,
        coalesce(oia.total_units_count, 0) as total_units_count,
        coalesce(oia.gross_amount, 0) as gross_amount,
        coalesce(oia.total_discount_amount, 0) as total_discount_amount,
        coalesce(oia.net_amount, 0) as net_amount,
        case when o.status = 'completed' then true else false end as is_completed_order
    from orders o
    left join order_items_aggregated oia
        on o.order_id = oia.order_id
)

select * from final
