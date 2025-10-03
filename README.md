# Rakuten Product Search Data Pipeline

楽天商品検索APIを使用して商品データを取得し、GCSに保存後、dbtでクレンジングしてPostgreSQLに格納するデータパイプラインです。

## 特徴

- **楽天API統合**: 楽天商品検索APIから商品情報を自動取得
- **GCSストレージ**: 生データをJSONL形式でクラウドストレージに保存
- **dbt変換**: 4層アーキテクチャ（raw/staging/intermediate/mart）でデータクレンジング
- **PostgreSQL**: 外部公開されたデータベースで分析用データを提供
- **Terraform管理**: GCPリソースをInfrastructure as Codeで管理
- **レート制限対応**: APIリクエスト間隔を調整可能

## アーキテクチャ

```
楽天API → Python Script → GCS (JSONL形式)
                             ↓
                    load_gcs_to_postgres.py
                             ↓
                      PostgreSQL (Port 5432)
              ┌──────────┴──────────┬──────────┬──────────┐
             raw              staging      intermediate    mart
        (JSONB生データ)    (正規化)      (ビジネスロジック) (分析用)
```

## データフロー

1. **データ収集**: Pythonスクリプトが楽天APIから商品データを取得
2. **ストレージ**: JSONL形式でGCSバケットに保存
3. **ロード**: `load_gcs_to_postgres.py`がGCSからダウンロードしてPostgreSQLのrawテーブルに投入
4. **変換**: dbtがraw → staging → intermediate → martの順で変換
5. **分析**: PostgreSQL（localhost:5432）に直接接続してデータ分析

## ディレクトリ構造

```
rakuten_search/
├── .doc/                    # 設計文書・タスク管理
├── terraform/               # GCPインフラ定義
│   ├── modules/            # 再利用可能なモジュール
│   └── environments/dev/   # 開発環境設定
├── python-search/          # 楽天API検索スクリプト
├── dbt-project/            # dbtプロジェクト
│   ├── models/
│   │   ├── raw/           # GCSからロードした生データ
│   │   ├── staging/       # クレンジング済みデータ
│   │   ├── intermediate/  # ビジネスロジック適用
│   │   └── mart/          # 分析用最終テーブル
│   └── scripts/           # ヘルパースクリプト
└── docker-compose.yml      # コンテナオーケストレーション
```

## 技術スタック

- **言語**: Python 3.12
- **データベース**: PostgreSQL 16
- **変換ツール**: dbt 1.7
- **クラウド**: Google Cloud Platform (GCS)
- **IaC**: Terraform >= 1.0
- **コンテナ**: Docker & Docker Compose

## 前提条件

- Docker & Docker Compose がインストールされていること
- Terraform >= 1.0 がインストールされていること
- GCPアカウントと課金が有効なプロジェクト
- 楽天デベロッパーアカウントとAPIキー（[取得方法](https://webservice.rakuten.co.jp/guide/)）
- 十分なディスク容量（PostgreSQLデータ用）

## セットアップ

### 1. GCPインフラの作成

```bash
# Terraformディレクトリに移動
cd terraform/environments/dev

# terraform.tfvarsを編集
# project_id, bucket_name等を設定

# 初期化
terraform init

# プレビュー
terraform plan

# 適用
terraform apply
```

サービスアカウントキーは以下のコマンドで取得できます:

```bash
# 出力されたbase64エンコードされたキーをデコード
terraform output -raw service_account_key | base64 -d > ../../../credentials/service-account-key.json
```

### 2. 環境変数の設定

```bash
# .env.exampleをコピー
cp .env.example .env

# .envファイルを編集し、以下を設定:
# - RAKUTEN_API_KEY
# - GCP_PROJECT_ID
# - GCS_BUCKET_NAME
# - POSTGRES_PASSWORD
```

### 3. GCP認証情報の配置

```bash
# credentialsディレクトリを作成
mkdir -p credentials

# Terraformから取得したサービスアカウントキーを配置
# credentials/service-account-key.json
```

### 4. Dockerサービスの起動

```bash
# PostgreSQLを起動
docker-compose up -d postgres

# ヘルスチェック
docker-compose ps
```

## 使い方

### データパイプライン実行手順

#### 1. 楽天APIから商品データを取得

```bash
# 検索キーワードや取得ページ数は.envファイルで設定可能
# SEARCH_KEYWORD: 検索キーワード（デフォルト: ノートパソコン）
# MAX_PAGES: 取得ページ数（デフォルト: 10）
# REQUEST_DELAY: リクエスト間隔（秒、デフォルト: 1.0）

docker-compose --profile search run --rm python-search
```

**実行結果例:**
```
2025-10-03 17:04:26,761 - __main__ - INFO - Searching for 'ノートパソコン' (page 1)
2025-10-03 17:04:26,931 - __main__ - INFO - Retrieved 30 items from page 1
...
2025-10-03 17:04:37,885 - __main__ - INFO - Uploaded 300 items to gs://bucket-name/rakuten_products_20251003_170426.jsonl
2025-10-03 17:04:37,885 - __main__ - INFO - Total items collected: 300
```

#### 2. GCSからPostgreSQLへデータロード

```bash
# GCSから最新のJSONLファイルをダウンロードしてPostgreSQLのrawテーブルに投入
docker-compose --profile dbt run --rm dbt python scripts/load_gcs_to_postgres.py
```

**実行結果例:**
```
Downloading latest file from GCS...
Downloaded: rakuten_products_20251003_170426.jsonl -> /tmp/gcs_data/rakuten_products_20251003_170426.jsonl
Loading data to PostgreSQL...
Loaded 300 records into public_raw.rakuten_products_raw
Success!
```

#### 3. dbtでデータ変換

```bash
# dbtモデルを実行 (raw → staging → intermediate → mart)
docker-compose --profile dbt run --rm dbt dbt run
```

**実行結果例:**
```
17:21:42  1 of 4 OK created sql table model public_raw.rakuten_products_raw .............. [SELECT 300 in 0.05s]
17:21:42  2 of 4 OK created sql view model public_staging.stg_rakuten_products ........... [CREATE VIEW in 0.02s]
17:21:42  3 of 4 OK created sql view model public_intermediate.int_products_enriched ..... [CREATE VIEW in 0.02s]
17:21:42  4 of 4 OK created sql table model public_mart.dim_products ..................... [SELECT 300 in 0.07s]
Completed successfully
Done. PASS=4 WARN=0 ERROR=0 SKIP=0 TOTAL=4
```

#### 4. dbtテスト実行（オプション）

```bash
# データ品質テストを実行
docker-compose --profile dbt run --rm dbt dbt test
```

#### 5. dbtドキュメント生成（オプション）

```bash
# dbtドキュメントを生成
docker-compose --profile dbt run --rm dbt dbt docs generate

# ドキュメントサーバーを起動（http://localhost:8080）
docker-compose --profile dbt run --rm dbt dbt docs serve --port 8080
```

### PostgreSQLへの接続

PostgreSQLはポート5432で外部公開されているため、直接接続できます。

#### コマンドラインから接続

```bash
# psqlで接続（ローカルにpsqlがある場合）
PGPASSWORD=datauser psql -h localhost -p 5432 -U datauser -d rakuten_data

# データ確認
\dt public_mart.*                                    # martスキーマのテーブル一覧
SELECT COUNT(*) FROM public_mart.dim_products;      # レコード数確認
SELECT * FROM public_mart.dim_products LIMIT 5;     # サンプルデータ確認
```

#### GUIクライアントで接続

DBeaver、pgAdmin、TablePlusなどのGUIツールで接続:

| 項目 | 値 |
|------|-----|
| Host | `localhost` |
| Port | `5432` |
| Database | `rakuten_data` |
| User | `datauser` |
| Password | `.env`ファイルで設定した`POSTGRES_PASSWORD` |

#### データ確認クエリ例

```sql
-- 商品数確認
SELECT COUNT(*) FROM public_mart.dim_products;

-- 価格帯別の商品数
SELECT price_category, COUNT(*)
FROM public_mart.dim_products
GROUP BY price_category;

-- 高評価商品の抽出
SELECT item_name, item_price, review_average, review_count
FROM public_mart.dim_products
WHERE is_highly_rated = true
ORDER BY review_average DESC, review_count DESC
LIMIT 10;

-- ショップ別商品数
SELECT shop_name, COUNT(*) as product_count
FROM public_mart.dim_products
GROUP BY shop_name
ORDER BY product_count DESC
LIMIT 10;
```

## dbtモデルレイヤリング

このプロジェクトでは、dbtのベストプラクティスに従った4層アーキテクチャを採用しています。

### 📥 raw（生データ層）

**テーブル**: `public_raw.rakuten_products_raw`

- **目的**: GCSからダウンロードしたJSONLデータをそのまま格納
- **データ形式**: JSONB型で全フィールドを保持
- **ロード方法**: `load_gcs_to_postgres.py`スクリプトで投入
- **マテリアライズ**: テーブル

**カラム構成**:
```sql
data      JSONB       -- 楽天APIのレスポンスJSON
loaded_at TIMESTAMP   -- データロード日時
```

### 🧹 staging（ステージング層）

**ビュー**: `public_staging.stg_rakuten_products`

- **目的**: 基本的なデータクレンジングと正規化
- **マテリアライズ**: ビュー（軽量・常に最新）

**主な処理**:
- JSONBからフィールド抽出（50以上のフィールド）
- データ型変換（文字列→数値、タイムスタンプ）
- NULL処理（NULLIF関数で空文字列をNULLに変換）
- カラム名標準化（スネークケース）

**抽出フィールド例**:
- `item_code`, `item_name`, `item_price`
- `shop_code`, `shop_name`
- `review_count`, `review_average`
- `point_rate`, `point_rate_start_time`, `point_rate_end_time`

### 🔄 intermediate（中間層）

**ビュー**: `public_intermediate.int_products_enriched`

- **目的**: ビジネスロジックの適用と計算フィールドの追加
- **マテリアライズ**: ビュー

**計算フィールド**:

| フィールド | 説明 | ロジック |
|-----------|------|---------|
| `estimated_points` | 推定獲得ポイント | `item_price × point_rate ÷ 100` |
| `price_category` | 価格帯分類 | `low`(<5,000円) / `medium`(<20,000円) / `high`(<50,000円) / `premium`(50,000円~) |
| `is_highly_rated` | 高評価フラグ | レビュー10件以上 かつ 平均4.0以上 |
| `shipping_type` | 配送タイプ | `free_shipping` / `next_day` / `standard` |
| `effective_price` | 実効価格 | 価格 - 推定ポイント |

### 📊 mart（マート層）

**テーブル**: `public_mart.dim_products`

- **目的**: 分析用の最終テーブル（ディメンションテーブル）
- **マテリアライズ**: テーブル（パフォーマンス最適化）

**主なカラム**:
```sql
item_code           VARCHAR   -- 商品コード（主キー）
item_name           VARCHAR   -- 商品名
item_price          INTEGER   -- 価格
effective_price     INTEGER   -- 実効価格
price_category      VARCHAR   -- 価格カテゴリ
shop_code           VARCHAR   -- ショップコード
shop_name           VARCHAR   -- ショップ名
review_count        INTEGER   -- レビュー数
review_average      DECIMAL   -- レビュー平均
is_highly_rated     BOOLEAN   -- 高評価フラグ
shipping_type       VARCHAR   -- 配送タイプ
loaded_at           TIMESTAMP -- ロード日時
processed_at        TIMESTAMP -- 処理日時
```

**用途**:
- BIツール（Looker、Tableau等）からの参照
- アドホック分析
- レポート生成

## トラブルシューティング

### PostgreSQL接続エラー

**症状**: `connection refused`や接続タイムアウト

```bash
# PostgreSQLコンテナの状態確認
docker-compose ps postgres

# PostgreSQLのヘルスチェック
docker-compose exec postgres pg_isready -U datauser

# ログ確認
docker-compose logs postgres

# ポート5432が使用されているか確認
lsof -i :5432

# コンテナ再起動
docker-compose restart postgres
```

### 楽天APIレート制限エラー

**症状**: `HTTP 429 Too Many Requests`

```bash
# .envファイルでリクエスト間隔を調整
REQUEST_DELAY=2.0  # 1.0秒から2.0秒に増やす

# または取得ページ数を減らす
MAX_PAGES=5  # 10ページから5ページに減らす
```

### dbt実行エラー

**症状**: モデル実行時にエラー

```bash
# dbt接続テスト
docker-compose --profile dbt run --rm dbt dbt debug

# SQLコンパイル確認
docker-compose --profile dbt run --rm dbt dbt compile

# 特定モデルのみ実行
docker-compose --profile dbt run --rm dbt dbt run --select stg_rakuten_products

# フルリフレッシュ（テーブル再作成）
docker-compose --profile dbt run --rm dbt dbt run --full-refresh
```

### GCS接続エラー

**症状**: `403 Forbidden`や認証エラー

```bash
# 認証情報ファイルの存在確認
ls -la credentials/service-account-key.json

# GCSバケットへのアクセステスト
gsutil ls gs://your-bucket-name/

# サービスアカウントの権限確認
gcloud projects get-iam-policy your-project-id \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:your-sa@your-project.iam.gserviceaccount.com"

# 必要な権限: roles/storage.objectAdmin
```

### データロードエラー

**症状**: `load_gcs_to_postgres.py`実行時のエラー

```bash
# 環境変数の確認
docker-compose --profile dbt run --rm dbt env | grep -E "GCS_|POSTGRES_"

# GCSに最新ファイルが存在するか確認
gsutil ls -l gs://your-bucket-name/rakuten_products_*.jsonl | tail -5

# 手動でPostgreSQLテーブル確認
docker-compose exec postgres psql -U datauser -d rakuten_data -c "\dt public_raw.*"
```

### ディスク容量不足

**症状**: `no space left on device`

```bash
# Dockerのディスク使用量確認
docker system df

# 未使用のイメージ・コンテナ・ボリュームを削除
docker system prune -a

# PostgreSQLボリュームのサイズ確認
docker volume ls
docker volume inspect rakuten_search_postgres_data
```

## 設定のカスタマイズ

### 検索条件の変更

`.env`ファイルで以下のパラメータをカスタマイズできます:

```bash
# 検索キーワード
SEARCH_KEYWORD=タブレット

# 1ページあたりの取得件数（最大30）
HITS_PER_PAGE=30

# 取得ページ数
MAX_PAGES=20

# APIリクエスト間隔（秒）
REQUEST_DELAY=1.5

# 出力ファイル名のプレフィックス
OUTPUT_PREFIX=rakuten_products
```

### GCSライフサイクル設定

Terraformで古いファイルを自動削除:

```hcl
# terraform/environments/dev/terraform.tfvars
gcs_lifecycle_rules = [
  {
    action = {
      type = "Delete"
    }
    condition = {
      age = 90  # 90日以上経過したファイルを削除
    }
  }
]
```

### PostgreSQL接続設定

```bash
# .envファイル
POSTGRES_DB=rakuten_data
POSTGRES_USER=datauser
POSTGRES_PASSWORD=your_secure_password  # 強固なパスワードに変更
```

## セキュリティ考慮事項

### 本番環境への適用時の注意

このプロジェクトは開発・検証環境向けに設計されています。本番環境で使用する場合は以下の対策を検討してください:

1. **PostgreSQLへのアクセス制限**
   - ファイアウォール設定（特定IPからのみアクセス許可）
   - VPN経由でのアクセス
   - SSL/TLS接続の強制

2. **認証情報の管理**
   - `.env`ファイルを`.gitignore`に含める（設定済み）
   - GCPサービスアカウントキーを安全に管理
   - パスワードローテーション

3. **データ暗号化**
   - PostgreSQLの暗号化設定
   - GCSバケットの暗号化（デフォルトで有効）

4. **ログ監視**
   - Cloud Loggingでアクセスログを監視
   - 異常なアクセスパターンの検出

## クリーンアップ

### Dockerリソースの削除

```bash
# コンテナとネットワークの停止・削除
docker-compose down

# ボリュームも含めて完全削除（データベースのデータも削除されます）
docker-compose down -v

# イメージも削除
docker-compose down --rmi all
```

### GCPリソースの削除

```bash
# Terraformで作成したリソースを削除
cd terraform/environments/dev
terraform destroy

# 削除前に確認
terraform plan -destroy
```

**注意**: `terraform destroy`は以下を削除します:
- GCSバケット（`force_destroy=true`の場合、中のファイルも削除）
- サービスアカウント
- IAMポリシーバインディング

## よくある質問（FAQ）

### Q: 楽天APIキーはどこで取得できますか？

A: [楽天デベロッパーサイト](https://webservice.rakuten.co.jp/)でアカウント登録後、アプリケーションIDを取得できます。

### Q: どのくらいのデータ量を扱えますか？

A: デフォルト設定（10ページ×30件=300件）で問題なく動作します。大量データの場合はPostgreSQLのリソース（メモリ、ディスク）を調整してください。

### Q: データの更新頻度はどうすればいいですか？

A: cronやAirflowで定期実行を設定できます。楽天のデータ更新頻度に応じて、1日1回~週1回程度が推奨です。

### Q: 他のECサイトAPIに対応できますか？

A: `python-search/search.py`を修正することで、Amazon PA-APIやYahoo!ショッピングAPIなどにも対応可能です。

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずIssueで議論してください。

## 参考リンク

- [楽天商品検索API ドキュメント](https://webservice.rakuten.co.jp/documentation/ichiba-item-search)
- [dbt Documentation](https://docs.getdbt.com/)
- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
