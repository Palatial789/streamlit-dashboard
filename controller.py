import streamlit as st

from model import load_data, predict_cluster, train_cluster_model
from view import (
    render_app_styles,
    render_clustering_dashboard,
    render_page_header,
    render_performance_dashboard,
)


def run_app():
    st.set_page_config(
        page_title="Dashboard Engagement",
        page_icon="📊",
        layout="wide",
    )
    render_app_styles()
    data = load_data()

    st.sidebar.markdown("## 📊 Insight Sosial")
    st.sidebar.caption("Dashboard performa dan engagement")
    selected_page = st.sidebar.radio(
        "Navigasi",
        ["Dashboard performa", "Clustering engagement"],
    )

    if selected_page == "Dashboard performa":
        render_page_header(
            "Performa Media Sosial",
            "Pantau engagement rate, impression bulanan, dan performa tahunan.",
        )
        render_performance_dashboard(data)
        return

    clustering_result = train_cluster_model(data)

    def handle_cluster_prediction(raw_input):
        return predict_cluster(raw_input, clustering_result)

    render_clustering_dashboard(
        data,
        clustering_result,
        handle_cluster_prediction,
    )
