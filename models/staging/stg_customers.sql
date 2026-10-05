with source as (
    select * from {{ ref('raw_customers') }}
),

renamed as (
    select
        cast(customer_id as int64) as customer_id,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        concat(trim(first_name), ' ', trim(last_name)) as full_name,
        lower(trim(email)) as email,
        trim(city) as city,
        trim(country) as country,
        cast(signup_date as date) as signup_date
    from source
)

select * from renamed
