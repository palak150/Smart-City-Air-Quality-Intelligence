# Databricks notebook source
# MAGIC %md
# MAGIC # Smart City – Air Quality Intelligence
# MAGIC
# MAGIC PySpark implementation of the Raw → Bronze → Silver → Gold pipeline.
# MAGIC The input CSV is synthetic demonstration data, not official CPCB/live data.
# MAGIC
# MAGIC Before running: create a Unity Catalog Volume and upload
# MAGIC `air_quality_demo.csv` to `/Volumes/<catalog>/<schema>/<volume>/air_quality_demo.csv`.
# MAGIC Update the notebook widgets below to match your catalog, schema and file path.

# COMMAND ----------
# Widgets: update defaults if your catalog/schema/volume names differ.
dbutils.widgets.text("catalog", "main", "Catalog")
dbutils.widgets.text("schema", "default", "Schema")
dbutils.widgets.text(
    "raw_path",
    "/Volumes/main/default/air_quality/air_quality_demo.csv",
    "Raw CSV path"
)

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
raw_path = dbutils.widgets.get("raw_path")

# Validate and create the target schema.
spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{schema}`")
spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA `{schema}`")

# COMMAND ----------
# 1. BRONZE: load the original CSV and preserve source columns.
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType

raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(raw_path)
)

required_columns = [
    "date", "hour", "city", "station",
    "aqi", "pm25", "pm10", "no2", "so2", "co"
]
missing_columns = [c for c in required_columns if c not in raw_df.columns]
if missing_columns:
    raise ValueError(f"CSV is missing required columns: {missing_columns}")

bronze_table = f"{catalog}.{schema}.bronze_air_quality"
(raw_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(bronze_table))

print(f"Bronze rows: {spark.table(bronze_table).count()}")
display(spark.table(bronze_table).limit(10))

# COMMAND ----------
# 2. SILVER: standardize types, remove incomplete/invalid rows and add month.
bronze = spark.table(bronze_table)

silver = (
    bronze
    .withColumn("date", F.to_date(F.col("date")))
    .withColumn("hour", F.col("hour").cast(IntegerType()))
    .withColumn("aqi", F.col("aqi").cast(DoubleType()))
    .withColumn("pm25", F.col("pm25").cast(DoubleType()))
    .withColumn("pm10", F.col("pm10").cast(DoubleType()))
    .withColumn("no2", F.col("no2").cast(DoubleType()))
    .withColumn("so2", F.col("so2").cast(DoubleType()))
    .withColumn("co", F.col("co").cast(DoubleType()))
)

for column in required_columns:
    silver = silver.filter(F.col(column).isNotNull())

silver = (
    silver
    .filter((F.col("aqi") >= 0) & (F.col("aqi") <= 500))
    .withColumn("month", F.date_format("date", "yyyy-MM"))
)

silver_table = f"{catalog}.{schema}.silver_air_quality"
(silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(silver_table))

print(f"Silver rows: {spark.table(silver_table).count()}")
display(spark.table(silver_table).limit(10))

# COMMAND ----------
# 3. GOLD: city-level summary.
clean = spark.table(silver_table)

city_summary = (
    clean.groupBy("city")
    .agg(
        F.round(F.avg("aqi"), 2).alias("avg_aqi"),
        F.max("aqi").alias("max_aqi"),
        F.round(F.avg("pm25"), 2).alias("avg_pm25"),
        F.round(F.avg("pm10"), 2).alias("avg_pm10"),
        F.round(F.avg("no2"), 2).alias("avg_no2"),
        F.round(F.avg("so2"), 2).alias("avg_so2"),
        F.round(F.avg("co"), 2).alias("avg_co"),
        F.count("aqi").alias("observations")
    )
    .withColumn(
        "aqi_band",
        F.when(F.col("avg_aqi") <= 50, "Good")
         .when(F.col("avg_aqi") <= 100, "Satisfactory")
         .when(F.col("avg_aqi") <= 200, "Moderate")
         .when(F.col("avg_aqi") <= 300, "Poor")
         .when(F.col("avg_aqi") <= 400, "Very Poor")
         .otherwise("Severe")
    )
    .orderBy(F.desc("avg_aqi"))
)

city_summary_table = f"{catalog}.{schema}.gold_city_summary"
(city_summary.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(city_summary_table))
display(spark.table(city_summary_table))

# COMMAND ----------
# 4. GOLD: daily AQI trend by city.
daily = (
    clean.groupBy("date", "city")
    .agg(
        F.round(F.avg("aqi"), 2).alias("avg_aqi"),
        F.max("aqi").alias("max_aqi"),
        F.count("aqi").alias("observations")
    )
)
daily_table = f"{catalog}.{schema}.gold_city_daily_aqi"
(daily.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(daily_table))
display(spark.table(daily_table).orderBy("date", "city"))

# COMMAND ----------
# 5. GOLD: monthly trend by city.
monthly = (
    clean.groupBy("month", "city")
    .agg(F.round(F.avg("aqi"), 2).alias("avg_aqi"))
)
monthly_table = f"{catalog}.{schema}.gold_monthly_trend"
(monthly.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(monthly_table))
display(spark.table(monthly_table).orderBy("month", "city"))

# COMMAND ----------
# 6. GOLD: average value for each pollutant.
pollutant_summary = (
    clean.select(
        F.expr("stack(5, 'PM2.5', pm25, 'PM10', pm10, 'NO2', no2, 'SO2', so2, 'CO', co) "
               "as (pollutant, value)")
    )
    .groupBy("pollutant")
    .agg(F.round(F.avg("value"), 2).alias("average_value"))
    .orderBy("pollutant")
)
pollutant_table = f"{catalog}.{schema}.gold_pollutant_summary"
(pollutant_summary.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(pollutant_table))
display(spark.table(pollutant_table))

# COMMAND ----------
# Pipeline completion summary.
for table_name in [
    bronze_table, silver_table, city_summary_table,
    daily_table, monthly_table, pollutant_table
]:
    print(f"{table_name}: {spark.table(table_name).count()} rows")
