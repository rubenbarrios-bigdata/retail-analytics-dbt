-- Análisis ad-hoc de rendimiento mensual de ventas y tasa de cancelación
select
    order_year_month,
    count(order_id) as total_orders,
    countif(is_completed_order) as completed_orders,
    round(safe_divide(countif(is_completed_order), count(order_id)) * 100, 2) as completion_rate_pct,
    round(sum(case when is_completed_order then gross_amount else 0 end), 2) as gross_revenue,
    round(sum(case when is_completed_order then total_discount_amount else 0 end), 2) as total_discounts,
    round(sum(case when is_completed_order then net_amount else 0 end), 2) as net_revenue,
    round(safe_divide(sum(case when is_completed_order then net_amount else 0 end), countif(is_completed_order)), 2) as monthly_aov
from {{ ref('fct_orders') }}
group by 1
order by 1 desc
