-- Catálogo Analítico de Productos: Consolida ventas acumuladas, ingresos y margen de ganancia comercial
with products as (
    select * from {{ ref('stg_products') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

product_sales_aggregated as (
    select
        oi.product_id,
        count(distinct oi.order_id) as total_orders_count,
        sum(oi.quantity) as total_units_sold,
        round(sum(case when o.status = 'completed' then oi.item_gross_amount else 0 end), 2) as total_gross_revenue,
        round(sum(case when o.status = 'completed' then oi.discount_amount else 0 end), 2) as total_discounts_applied,
        round(sum(case when o.status = 'completed' then oi.item_net_amount else 0 end), 2) as total_net_revenue
    from order_items oi
    inner join orders o
        on oi.order_id = o.order_id
    group by oi.product_id
),

final as (
    select
        p.product_id,
        p.product_name,
        p.category,
        p.cost_price,
        p.list_price,
        p.unit_margin,
        p.margin_percentage,
        coalesce(psa.total_orders_count, 0) as total_orders_count,
        coalesce(psa.total_units_sold, 0) as total_units_sold,
        coalesce(psa.total_gross_revenue, 0) as total_gross_revenue,
        coalesce(psa.total_discounts_applied, 0) as total_discounts_applied,
        coalesce(psa.total_net_revenue, 0) as total_net_revenue,
        round(coalesce(psa.total_net_revenue, 0) - (coalesce(psa.total_units_sold, 0) * p.cost_price), 2) as total_estimated_profit
    from products p
    left join product_sales_aggregated psa
        on p.product_id = psa.product_id
)

select * from final
