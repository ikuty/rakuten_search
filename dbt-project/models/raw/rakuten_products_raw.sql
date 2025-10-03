{{
  config(
    materialized='table',
    pre_hook="CREATE TABLE IF NOT EXISTS {{ this }} (data JSONB, loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
  )
}}

-- GCSからダウンロードしたJSONLファイルを読み込むrawテーブル
-- 注意: 実際のデータロードはdbt run実行前に別途行う必要があります
--
-- 手順:
-- 1. python-search でGCSにデータをアップロード
-- 2. dbt-project/scripts/download_from_gcs.py を手動で実行してローカルにダウンロード
-- 3. PostgreSQLのCOPYコマンドでテーブルにロード
-- 4. dbt run を実行して staging/intermediate/mart を生成
--
-- このモデルは既存のrawテーブルからデータを取得します

SELECT
    data,
    loaded_at
FROM {{ this }}
