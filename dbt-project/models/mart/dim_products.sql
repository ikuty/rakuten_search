{{
  config(
    materialized='table'
  )
}}

WITH products AS (
    SELECT * FROM {{ ref('int_products_enriched') }}
),

final AS (
    SELECT
        -- Primary key
        item_code,

        -- Product information
        item_name,
        item_url,
        item_caption,
        catchcopy,

        -- Pricing
        item_price,
        effective_price,
        estimated_points,
        price_category,

        -- Shop information
        shop_code,
        shop_name,
        shop_url,

        -- Category
        genre_id,

        -- Review metrics
        review_count,
        review_average,
        is_highly_rated,

        -- Shipping
        shipping_type,
        availability,
        postage_flag,
        asuraku_flag,
        ship_overseas_flag,

        -- Points
        point_rate,
        point_rate_start_time,
        point_rate_end_time,

        -- Affiliate
        affiliate_url,
        affiliate_rate,

        -- Metadata
        loaded_at,
        CURRENT_TIMESTAMP AS processed_at

    FROM products
)

SELECT * FROM final
