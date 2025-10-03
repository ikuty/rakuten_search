{{
  config(
    materialized='view'
  )
}}

WITH products AS (
    SELECT * FROM {{ ref('stg_rakuten_products') }}
),

enriched AS (
    SELECT
        *,

        -- Price calculations
        CASE
            WHEN item_price > 0 THEN ROUND(item_price * point_rate / 100.0, 0)
            ELSE 0
        END AS estimated_points,

        -- Price category
        CASE
            WHEN item_price < 5000 THEN 'low'
            WHEN item_price < 20000 THEN 'medium'
            WHEN item_price < 50000 THEN 'high'
            ELSE 'premium'
        END AS price_category,

        -- Review quality flag
        CASE
            WHEN review_count >= 10 AND review_average >= 4.0 THEN true
            ELSE false
        END AS is_highly_rated,

        -- Shipping convenience
        CASE
            WHEN postage_flag = 0 THEN 'free_shipping'
            WHEN asuraku_flag = 1 THEN 'next_day'
            ELSE 'standard'
        END AS shipping_type,

        -- Calculate effective price (after points)
        CASE
            WHEN item_price > 0 THEN item_price - ROUND(item_price * point_rate / 100.0, 0)
            ELSE item_price
        END AS effective_price

    FROM products
)

SELECT * FROM enriched
