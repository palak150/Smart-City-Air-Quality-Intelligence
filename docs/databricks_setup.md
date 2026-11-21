# Databricks setup and execution

This folder adds a Databricks + PySpark implementation alongside the existing local
Pandas pipeline and Streamlit dashboard. The two paths use the same CSV schema and
produce equivalent analytics at a high level; they are separate execution environments.

## Prerequisites

- Access to a Databricks workspace with permission to use compute and Unity Catalog.
- A catalog and schema you are allowed to create/use.
- A Unity Catalog Volume in that schema, or another accessible storage location.

## 1. Create a Volume

In a Databricks SQL editor, adjust the catalog/schema if needed and run:

```sql
CREATE SCHEMA IF NOT EXISTS main.default;
CREATE VOLUME IF NOT EXISTS main.default.air_quality;
```

If your workspace does not permit creating a volume, ask your workspace administrator
for an approved upload location. Do not put credentials or access tokens in this repository.

## 2. Upload the demo CSV

Upload this repository file:

`data/raw/air_quality_demo.csv`

to the Volume path:

`/Volumes/main/default/air_quality/air_quality_demo.csv`

If you use a different catalog/schema/volume, note the full path for the notebook parameter.

## 3. Import and run the PySpark notebook

1. In the Databricks workspace, choose **Workspace** → **Import**.
2. Import `databricks/notebooks/01_air_quality_medallion_pipeline.py`.
3. Attach the notebook to available compute (or serverless compute if enabled).
4. Set the notebook parameters:
   - `catalog`: `main`
   - `schema`: `default`
   - `raw_path`: `/Volumes/main/default/air_quality/air_quality_demo.csv`
5. Run all cells from top to bottom.

The notebook creates these Delta tables:

| Layer | Table | Purpose |
|---|---|---|
| Bronze | `main.default.bronze_air_quality` | Raw ingested rows |
| Silver | `main.default.silver_air_quality` | Typed and cleaned rows |
| Gold | `main.default.gold_city_summary` | City KPIs and AQI band |
| Gold | `main.default.gold_city_daily_aqi` | Daily trend by city |
| Gold | `main.default.gold_monthly_trend` | Monthly trend by city |
| Gold | `main.default.gold_pollutant_summary` | Average pollutant values |

The notebook uses overwrite mode for repeatable demo runs. Do not use this pattern unchanged
for production ingestion where historical data must be retained.

## 4. Run Databricks SQL

Open `databricks/sql/air_quality_analytics.sql` in a Databricks SQL editor.
If you chose a different catalog/schema, replace `main.default` in the queries.

## 5. Build an AI/BI dashboard

In Databricks SQL:

1. Open **SQL Editor** and run the queries in `air_quality_analytics.sql`.
2. Save the useful queries.
3. Choose **Dashboards** → **Create dashboard** (AI/BI dashboard wording may vary by workspace).
4. Add visualizations based on the saved queries:
   - KPI tiles: overall average AQI, highest city maximum AQI, monitored cities, observations.
   - Bar chart: average AQI by city.
   - Line chart: daily AQI by date, grouped by city.
   - Line/bar chart: monthly AQI trend by city.
   - Bar chart: average value by pollutant.
5. Publish/share only if your workspace permissions allow it.

Dashboard menus and availability depend on your Databricks workspace edition and permissions.

## Local dashboard remains available

The existing Streamlit dashboard is unchanged. Run it locally with:

```bash
pip install -r requirements.txt
python src/local_pipeline.py
streamlit run app.py
```

## Data limitation

The included CSV is synthetic demonstration data. It is not official CPCB data,
not a live sensor feed, and should not be presented as measured real-world pollution.
