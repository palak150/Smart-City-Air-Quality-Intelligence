from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "air_quality_demo.csv"
SILVER_DIR = ROOT / "data" / "silver"
GOLD_DIR = ROOT / "data" / "gold"

REQUIRED = ["date", "hour", "city", "station", "aqi", "pm25", "pm10", "no2", "so2", "co"]

def main():
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(RAW)
    missing = [c for c in REQUIRED if c not in raw.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    clean = raw.dropna(subset=REQUIRED).copy()
    clean["date"] = pd.to_datetime(clean["date"], errors="coerce")
    for col in ["hour", "aqi", "pm25", "pm10", "no2", "so2", "co"]:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    clean = clean.dropna(subset=["date", "hour", "aqi", "pm25", "pm10", "no2", "so2", "co"])
    clean = clean[(clean["aqi"] >= 0) & (clean["aqi"] <= 500)]
    clean["month"] = clean["date"].dt.to_period("M").astype(str)
    clean.to_csv(SILVER_DIR / "air_quality_clean.csv", index=False)

    city_summary = clean.groupby("city", as_index=False).agg(
        avg_aqi=("aqi", "mean"), max_aqi=("aqi", "max"),
        avg_pm25=("pm25", "mean"), avg_pm10=("pm10", "mean"),
        avg_no2=("no2", "mean"), avg_so2=("so2", "mean"),
        avg_co=("co", "mean"), observations=("aqi", "count")
    )
    city_summary["avg_aqi"] = city_summary["avg_aqi"].round(2)
    city_summary["aqi_band"] = pd.cut(
        city_summary["avg_aqi"], bins=[-1, 50, 100, 200, 300, 400, 500],
        labels=["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    ).astype(str)
    city_summary = city_summary.sort_values("avg_aqi", ascending=False)

    daily = clean.groupby(["date", "city"], as_index=False).agg(
        avg_aqi=("aqi", "mean"), max_aqi=("aqi", "max"), observations=("aqi", "count")
    )
    daily["avg_aqi"] = daily["avg_aqi"].round(2)
    monthly = clean.groupby(["month", "city"], as_index=False).agg(avg_aqi=("aqi", "mean"))
    monthly["avg_aqi"] = monthly["avg_aqi"].round(2)

    pollutant = clean[["pm25", "pm10", "no2", "so2", "co"]].mean().rename("average_value").reset_index()
    pollutant.columns = ["pollutant", "average_value"]
    pollutant["average_value"] = pollutant["average_value"].round(2)

    city_summary.to_csv(GOLD_DIR / "city_summary.csv", index=False)
    daily.to_csv(GOLD_DIR / "city_daily_aqi.csv", index=False)
    monthly.to_csv(GOLD_DIR / "monthly_trend.csv", index=False)
    pollutant.to_csv(GOLD_DIR / "pollutant_summary.csv", index=False)

    print(f"Pipeline complete. Raw={len(raw)}, Silver={len(clean)}")
    print(city_summary.to_string(index=False))
    print(f"Gold outputs saved to: {GOLD_DIR}")

if __name__ == "__main__":
    main()
