{% macro calculate_margin_pct(list_price, cost_price) %}
    round(safe_divide(cast({{ list_price }} as numeric) - cast({{ cost_price }} as numeric), cast({{ list_price }} as numeric)) * 100, 2)
{% endmacro %}
