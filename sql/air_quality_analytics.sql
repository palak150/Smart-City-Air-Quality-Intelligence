-- Smart City – Air Quality Intelligence
-- Run after the Databricks PySpark notebook has completed.
-- Replace main.default if you selected a different catalog/schema.

-- 1. Overall KPI values
SELECT
  ROUND(AVG(avg_aqi), 2) AS overall_avg_aqi,
  MAX(max_aqi) AS highest_city_max_aqi,
  COUNT(DISTINCT city) AS monitored_cities,
  SUM(observations) AS total_observations
FROM main.default.gold_city_summary;

-- 2. City comparison / ranking
SELECT city, avg_aqi, max_aqi, aqi_band, observations
FROM main.default.gold_city_summary
ORDER BY avg_aqi DESC;

-- 3. Daily AQI trend
SELECT date, city, avg_aqi, max_aqi, observations
FROM main.default.gold_city_daily_aqi
ORDER BY date, city;

-- 4. Monthly AQI trend
SELECT month, city, avg_aqi
FROM main.default.gold_monthly_trend
ORDER BY month, city;

-- 5. Pollutant comparison
SELECT pollutant, average_value
FROM main.default.gold_pollutant_summary
ORDER BY average_value DESC;

-- 6. Highest-AQI city (based on average AQI)
SELECT city, avg_aqi, aqi_band
FROM main.default.gold_city_summary
ORDER BY avg_aqi DESC
LIMIT 1;
