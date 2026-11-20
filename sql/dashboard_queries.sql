-- Adapt table names to your Databricks catalog and schema.
-- Example table: main.default.gold_city_summary

-- 1. KPI values
SELECT
  ROUND(AVG(avg_aqi), 2) AS overall_avg_aqi,
  MAX(max_aqi) AS highest_aqi,
  COUNT(DISTINCT city) AS monitored_cities,
  SUM(observations) AS total_observations
FROM main.default.gold_city_summary;

-- 2. City comparison
SELECT city, avg_aqi, max_aqi, aqi_band
FROM main.default.gold_city_summary
ORDER BY avg_aqi DESC;

-- 3. Daily trend
SELECT date, city, avg_aqi
FROM main.default.gold_city_daily_aqi
ORDER BY date, city;

-- 4. Monthly trend
SELECT month, city, avg_aqi
FROM main.default.gold_monthly_trend
ORDER BY month, city;
