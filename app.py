from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
GOLD = ROOT / "data" / "gold"
SILVER = ROOT / "data" / "silver" / "air_quality_clean.csv"

st.set_page_config(page_title="Smart City | Air Quality Intelligence", page_icon="🌫️", layout="wide")

st.title("🌫️ Smart City – Air Quality Intelligence")
st.caption("Delhi NCR • City comparison, pollutant patterns and AQI trends")
st.warning("Demonstration dataset is synthetic; it is not official CPCB live measurement data.")

if not SILVER.exists() or not (GOLD / "city_summary.csv").exists():
    st.info("Analytics files are not generated yet. Run `python src/local_pipeline.py` in the project terminal, then refresh this page.")
    st.stop()

data = pd.read_csv(SILVER, parse_dates=["date"])
summary = pd.read_csv(GOLD / "city_summary.csv")
daily = pd.read_csv(GOLD / "city_daily_aqi.csv", parse_dates=["date"])
pollutants = pd.read_csv(GOLD / "pollutant_summary.csv")

with st.sidebar:
    st.header("Dashboard filters")
    cities = sorted(data["city"].unique().tolist())
    selected = st.multiselect("Select cities", cities, default=cities)
    min_date, max_date = data["date"].min().date(), data["date"].max().date()
    dates = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

if len(dates) == 2:
    start_date, end_date = dates
else:
    start_date, end_date = min_date, max_date

filtered = data[data["city"].isin(selected) & data["date"].dt.date.between(start_date, end_date)]
if filtered.empty:
    st.warning("No observations match the selected filters.")
    st.stop()

avg_aqi = filtered["aqi"].mean()
peak_aqi = filtered["aqi"].max()
city_count = filtered["city"].nunique()
obs_count = len(filtered)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Average AQI", f"{avg_aqi:.1f}")
k2.metric("Peak AQI", f"{peak_aqi:.0f}")
k3.metric("Cities monitored", f"{city_count}")
k4.metric("Observations", f"{obs_count:,}")

st.divider()
left, right = st.columns(2)
city_avg = filtered.groupby("city", as_index=False)["aqi"].mean().sort_values("aqi", ascending=True)
with left:
    st.subheader("City AQI ranking")
    fig = px.bar(city_avg, x="aqi", y="city", orientation="h", labels={"aqi":"Average AQI","city":"City"}, text_auto=".1f")
    fig.update_layout(yaxis_title="", xaxis_title="Average AQI")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Daily AQI trend")
    trend = filtered.groupby(["date", "city"], as_index=False)["aqi"].mean()
    fig = px.line(trend, x="date", y="aqi", color="city", markers=True, labels={"aqi":"Average AQI","date":"Date"})
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Pollutant comparison")
poll_cols = ["pm25", "pm10", "no2", "so2", "co"]
poll = filtered[poll_cols].mean().rename_axis("pollutant").reset_index(name="average_value")
fig = px.bar(poll, x="pollutant", y="average_value", color="pollutant", labels={"average_value":"Average concentration","pollutant":"Pollutant"})
st.plotly_chart(fig, use_container_width=True)

st.subheader("City-level details")
detail = filtered.groupby("city", as_index=False).agg(
    avg_aqi=("aqi","mean"), max_aqi=("aqi","max"), avg_pm25=("pm25","mean"),
    avg_pm10=("pm10","mean"), avg_no2=("no2","mean"), avg_so2=("so2","mean"),
    avg_co=("co","mean"), observations=("aqi","count")
).round(2).sort_values("avg_aqi", ascending=False)
st.dataframe(detail, use_container_width=True, hide_index=True)
st.caption("AQI bands in this demo are broad illustrative labels, not an official health advisory or CPCB calculation.")
