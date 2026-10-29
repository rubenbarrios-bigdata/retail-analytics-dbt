-- Perfilado Estadístico y de Segmentación Comercial sobre dim_customers
with customers as (
    select * from {{ ref('dim_customers') }}
)

select
    count(*) as total_customers,
    count(distinct customer_id) as unique_customers,
    countif(email is null) as null_emails,
    min(total_orders) as min_orders,
    max(total_orders) as max_orders,
    round(avg(total_orders), 1) as avg_orders,
    min(lifetime_spend) as min_spend,
    max(lifetime_spend) as max_spend,
    round(avg(lifetime_spend), 2) as avg_spend,
    countif(customer_segment = 'VIP') as segment_vip_count,
    countif(customer_segment = 'Frequent') as segment_frequent_count,
    countif(customer_segment = 'Active') as segment_active_count
from customers
