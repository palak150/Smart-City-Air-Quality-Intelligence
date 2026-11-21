from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
GOLD = ROOT / "data" / "gold"
SILVER = ROOT / "data" / "silver" / "air_quality_clean.csv"

st.set_page_config(page_title="Smart City | Air Quality Intelligence", page_icon="🌫️", layout="wide")


st.markdown("""
<style>
/* Main background */
.stApp {
    background: linear-gradient(135deg, #071421 0%, #10283A 55%, #0B1D2B 100%);
    color: #EAF4F7;
}

/* Main content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* Headings */
h1 {
    color: #F0FFFF !important;
    font-size: 2.5rem !important;
    font-weight: 800 !important;
}
h2, h3 {
    color: #65E5D2 !important;
    font-weight: 700 !important;
}

/* Caption and text */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #A8C2D1 !important;
}

/* KPI cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #16364B, #102638);
    border: 1px solid rgba(72, 214, 193, 0.35);
    border-radius: 18px;
    padding: 22px 20px;
    box-shadow: 0 6px 22px rgba(0, 0, 0, 0.22);
}
[data-testid="stMetricLabel"] {
    color: #B5CCD8 !important;
}
[data-testid="stMetricValue"] {
    color: #48D6C1 !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0C1D2C;
    border-right: 1px solid #23465A;
}
[data-testid="stSidebar"] h2 {
    color: #65E5D2 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #16B8A6, #39D6C2);
    color: #071923;
    border: none;
    border-radius: 10px;
    font-weight: 700;
}

/* Data table */
[data-testid="stDataFrame"] {
    border: 1px solid #286078;
    border-radius: 14px;
    overflow: hidden;
}

/* Dividers */
hr {
    border-color: #285064 !important;
}

/* Warning and info panels */
[data-testid="stAlert"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)
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
    fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(16,40,58,0.65)",
    font=dict(color="#EAF4F7", family="Arial"),
    title_font=dict(color="#65E5D2", size=20),
    margin=dict(l=15, r=15, t=35, b=15),
    xaxis=dict(showgrid=True, gridcolor="#29485B"),
    yaxis=dict(showgrid=False)
)
    st.plotly_chart(fig, use_container_width=True, theme=None)
with right:
    st.subheader("Daily AQI trend")
    trend = filtered.groupby(["date", "city"], as_index=False)["aqi"].mean()
    fig = px.line(trend, x="date", y="aqi", color="city", markers=True, labels={"aqi":"Average AQI","date":"Date"})
    st.plotly_chart(fig, use_container_width=True)
    fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(16,40,58,0.65)",
    font=dict(color="#EAF4F7", family="Arial"),
    margin=dict(l=15, r=15, t=35, b=15),
    xaxis=dict(showgrid=True, gridcolor="#29485B"),
    yaxis=dict(showgrid=True, gridcolor="#29485B")
)
st.subheader("Pollutant comparison")
poll_cols = ["pm25", "pm10", "no2", "so2", "co"]
poll = filtered[poll_cols].mean().rename_axis("pollutant").reset_index(name="average_value")
fig = px.bar(poll, x="pollutant", y="average_value", color="pollutant", labels={"average_value":"Average concentration","pollutant":"Pollutant"})
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(16,40,58,0.65)",
    font=dict(color="#EAF4F7", family="Arial"),
    margin=dict(l=15, r=15, t=35, b=15),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#29485B")
)
st.plotly_chart(fig, use_container_width=True, theme=None)
st.subheader("City-level details")
detail = filtered.groupby("city", as_index=False).agg(
    avg_aqi=("aqi","mean"), max_aqi=("aqi","max"), avg_pm25=("pm25","mean"),
    avg_pm10=("pm10","mean"), avg_no2=("no2","mean"), avg_so2=("so2","mean"),
    avg_co=("co","mean"), observations=("aqi","count")
).round(2).sort_values("avg_aqi", ascending=False)
st.dataframe(detail, use_container_width=True, hide_index=True)
st.caption("AQI bands in this demo are broad illustrative labels, not an official health advisory or CPCB calculation.")
