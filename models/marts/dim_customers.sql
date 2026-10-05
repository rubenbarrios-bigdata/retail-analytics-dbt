with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('fct_orders') }}
),

customer_orders_summary as (
    select
        customer_id,
        min(order_date) as first_order_date,
        max(order_date) as most_recent_order_date,
        count(order_id) as total_orders,
        countif(is_completed_order) as completed_orders,
        round(coalesce(sum(case when is_completed_order then net_amount else 0 end), 0), 2) as lifetime_spend,
        round(safe_divide(
            sum(case when is_completed_order then net_amount else 0 end),
            countif(is_completed_order)
        ), 2) as average_order_value
    from orders
    group by customer_id
),

final as (
    select
        c.customer_id,
        c.first_name,
        c.last_name,
        c.full_name,
        c.email,
        c.city,
        c.country,
        c.signup_date,
        cos.first_order_date,
        cos.most_recent_order_date,
        coalesce(cos.total_orders, 0) as total_orders,
        coalesce(cos.completed_orders, 0) as completed_orders,
        coalesce(cos.lifetime_spend, 0) as lifetime_spend,
        coalesce(cos.average_order_value, 0) as average_order_value,
        case
            when coalesce(cos.lifetime_spend, 0) >= 600 then 'VIP'
            when coalesce(cos.completed_orders, 0) >= 3 then 'Frequent'
            when coalesce(cos.completed_orders, 0) >= 1 then 'Active'
            else 'Prospect'
        end as customer_segment
    from customers c
    left join customer_orders_summary cos
        on c.customer_id = cos.customer_id
)

select * from final
