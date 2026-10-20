from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Engagement",
    page_icon="📊",
    layout="wide",
)

DATA_FILE = Path(__file__).parent / "data" / "bsd_2023_2025.csv"
INTERACTION_COLUMNS = ["Like", "Comment", "Share", "Save"]
MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
    "Jul", "Agu", "Sep", "Okt", "Nov", "Des",
]


@st.cache_data
def load_data():
    data = pd.read_csv(DATA_FILE)
    data["Interaksi"] = data[INTERACTION_COLUMNS].sum(axis=1)
    data["Engagement Rate"] = (
        data["Interaksi"].div(data["Total Impressions"].replace(0, pd.NA)) * 100
    ).fillna(0)
    data["Bulan"] = data["month_num"].map(lambda month: MONTH_NAMES[month - 1])
    return data


data = load_data()
years = sorted(data["year"].dropna().astype(int).unique())

st.title("Performa Media Sosial")
st.caption("Pantau engagement rate, impression bulanan, dan performa tahunan.")

selected_year = st.selectbox("Pilih tahun", years, index=len(years) - 1)
year_data = data[data["year"] == selected_year].sort_values("month_num")

total_impressions = year_data["Total Impressions"].sum()
total_interactions = year_data["Interaksi"].sum()
engagement_rate = (
    total_interactions / total_impressions * 100 if total_impressions else 0
)
total_posts = year_data["Total Post"].sum()

metric_columns = st.columns(4)
metric_columns[0].metric("Engagement rate", f"{engagement_rate:.2f}%")
metric_columns[1].metric("Total impression", f"{total_impressions:,.0f}")
metric_columns[2].metric("Total interaksi", f"{total_interactions:,.0f}")
metric_columns[3].metric("Total post", f"{total_posts:,.0f}")
st.caption("Engagement rate = (like + komentar + share + save) / impression.")

st.header(f"Impression bulanan · {selected_year}")
st.bar_chart(year_data, x="Bulan", y="Total Impressions", height=320)

st.header("Engagement rate bulanan")
st.line_chart(year_data, x="Bulan", y="Engagement Rate", height=280)

annual_summary = (
    data.groupby("year", as_index=False)
    .agg(
        Impression=("Total Impressions", "sum"),
        Interaksi=("Interaksi", "sum"),
        Post=("Total Post", "sum"),
        Follower_baru=("Follows", "sum"),
    )
    .sort_values("year")
)
annual_summary["Engagement Rate"] = (
    annual_summary["Interaksi"]
    .div(annual_summary["Impression"].replace(0, pd.NA))
    .mul(100)
    .fillna(0)
)

st.header("Ringkasan per tahun")
summary_left, summary_right = st.columns([1, 1])
with summary_left:
    st.dataframe(
        annual_summary.rename(columns={"year": "Tahun", "Follower_baru": "Follower baru"}),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Tahun": st.column_config.NumberColumn(format="%d"),
            "Impression": st.column_config.NumberColumn(format="%d"),
            "Interaksi": st.column_config.NumberColumn(format="%d"),
            "Post": st.column_config.NumberColumn(format="%d"),
            "Follower baru": st.column_config.NumberColumn(format="%d"),
            "Engagement Rate": st.column_config.NumberColumn(format="%.2f%%"),
        },
    )
with summary_right:
    st.bar_chart(annual_summary, x="year", y="Impression", height=280)
