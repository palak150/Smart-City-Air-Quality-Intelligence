# Smart City – Air Quality Intelligence

A small, ready-to-run project for exploring air-quality patterns across Delhi NCR.
It keeps the original project's core idea—raw data → cleaned data → analytics → dashboard—
while adding a lightweight local dashboard and a few distinct views.

## What's different in this version
- Uses a reproducible demo dataset with date, time slot and monitoring-station fields.
- Adds a city ranking and a selectable city/date dashboard filter.
- Includes a local Streamlit dashboard so you can preview results in a browser without first
  configuring Databricks.
- Keeps SQL analytics examples for a Databricks-style workflow.

## Important data note
`data/raw/air_quality_demo.csv` contains **synthetic demonstration data**. It is not official
CPCB, OpenAQ, or live sensor data. Do not present it as real-world measurements.

## Run on Windows (VS Code)
1. Install Python 3.10 or newer.
2. Open this project folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
5. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run this for the current terminal only:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```
   Then activate again.
6. Install packages:
   ```powershell
   pip install -r requirements.txt
   ```
7. Build the analytics outputs:
   ```powershell
   python src/local_pipeline.py
   ```
8. Launch the dashboard:
   ```powershell
   streamlit run app.py
   ```
   Streamlit will show a local URL, usually `http://localhost:8501`. Open it in your browser.

## Project structure
- `data/raw/air_quality_demo.csv` – synthetic demo observations
- `data/silver/` – cleaned observations created by the pipeline
- `data/gold/` – aggregated analytics created by the pipeline
- `src/local_pipeline.py` – cleaning and aggregation
- `app.py` – interactive local dashboard
- `sql/dashboard_queries.sql` – example SQL for Gold analytics
- `docs/data_dictionary.md` – fields and limitations

## Main dashboard views
- KPI cards: average AQI, peak AQI, cities covered, observations
- City ranking: average AQI by city
- Daily AQI trend by city
- Pollutant comparison
- City-level detail table

## Databricks
The SQL file provides starter queries. To use them in Databricks, upload the generated Gold
CSV files or write equivalent Delta tables in your workspace, then adapt table names to your
catalog and schema.
