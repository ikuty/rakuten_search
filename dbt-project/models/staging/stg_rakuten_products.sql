{{
  config(
    materialized='view'
  )
}}

WITH source AS (
    SELECT * FROM {{ ref('rakuten_products_raw') }}
),

flattened AS (
    SELECT
        -- Product identification
        (data->>'itemCode')::VARCHAR AS item_code,
        (data->>'itemName')::VARCHAR AS item_name,
        (data->>'itemUrl')::VARCHAR AS item_url,

        -- Pricing
        (data->>'itemPrice')::INTEGER AS item_price,
        (data->>'itemPriceBaseField')::VARCHAR AS price_base_field,
        (data->>'itemPriceMax1')::INTEGER AS price_max1,
        (data->>'itemPriceMin1')::INTEGER AS price_min1,
        (data->>'itemPriceMax2')::INTEGER AS price_max2,
        (data->>'itemPriceMin2')::INTEGER AS price_min2,

        -- Description
        (data->>'itemCaption')::TEXT AS item_caption,
        (data->>'catchcopy')::TEXT AS catchcopy,

        -- Media
        (data->>'mediumImageUrls')::JSONB AS medium_image_urls,
        (data->>'smallImageUrls')::JSONB AS small_image_urls,

        -- Shop information
        (data->>'shopCode')::VARCHAR AS shop_code,
        (data->>'shopName')::VARCHAR AS shop_name,
        (data->>'shopUrl')::VARCHAR AS shop_url,

        -- Categories
        (data->>'genreId')::VARCHAR AS genre_id,
        (data->>'tagIds')::JSONB AS tag_ids,

        -- Availability and shipping
        (data->>'availability')::INTEGER AS availability,
        (data->>'taxFlag')::INTEGER AS tax_flag,
        (data->>'postageFlag')::INTEGER AS postage_flag,
        (data->>'shipOverseasFlag')::INTEGER AS ship_overseas_flag,
        (data->>'shipOverseasArea')::VARCHAR AS ship_overseas_area,
        (data->>'asurakuFlag')::INTEGER AS asuraku_flag,
        (data->>'asurakuClosingTime')::VARCHAR AS asuraku_closing_time,

        -- Point information
        (data->>'pointRate')::INTEGER AS point_rate,
        NULLIF(data->>'pointRateStartTime', '')::TIMESTAMP AS point_rate_start_time,
        NULLIF(data->>'pointRateEndTime', '')::TIMESTAMP AS point_rate_end_time,

        -- Review information
        (data->>'reviewCount')::INTEGER AS review_count,
        (data->>'reviewAverage')::DECIMAL(3,2) AS review_average,

        -- Affiliate
        (data->>'affiliateUrl')::VARCHAR AS affiliate_url,
        (data->>'affiliateRate')::DECIMAL(5,2) AS affiliate_rate,

        -- Metadata
        loaded_at

    FROM source
)

SELECT * FROM flattened
