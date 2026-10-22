from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_samples,
    silhouette_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer, StandardScaler

DATA_FILE = Path(__file__).parent / "data" / "bsd_2023_2025.csv"
INTERACTION_COLUMNS = ["Like", "Comment", "Share", "Save"]
CLUSTER_FEATURES = [
    "Engagement_Rate",
    "Share_Rate",
    "Save_Rate",
    "Profile_Visit_Rate",
    "Website_Tap_Rate",
    "Follow_Conversion_Rate",
]
MONTH_NAMES = [
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
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


def build_cluster_features(data):
    features = data.copy()
    features["Engagement"] = features[INTERACTION_COLUMNS].sum(axis=1)
    features["Engagement_per_Post"] = (
        features["Engagement"].div(features["Total Post"].replace(0, np.nan))
    )
    features["Impressions_per_Post"] = (
        features["Total Impressions"].div(features["Total Post"].replace(0, np.nan))
    )
    features["Engagement_Rate"] = (
        features["Engagement"].div(features["Total Impressions"].replace(0, np.nan))
    )
    features["Profile_Visit_Rate"] = (
        features["Profile Visits"].div(features["Total Impressions"].replace(0, np.nan))
    )
    features["Website_Tap_Rate"] = (
        features["Website Taps"].div(features["Total Impressions"].replace(0, np.nan))
    )
    features["Follow_Conversion_Rate"] = (
        features["Follows"].div(features["Profile Visits"].replace(0, np.nan))
    )
    features["Share_Rate"] = (
        features["Share"].div(features["Total Impressions"].replace(0, np.nan))
    )
    features["Save_Rate"] = (
        features["Save"].div(features["Total Impressions"].replace(0, np.nan))
    )
    return features[CLUSTER_FEATURES].fillna(0)


@st.cache_resource
def train_cluster_model(training_data):
    features = build_cluster_features(training_data)
    preprocessor = Pipeline(
        [
            ("power", PowerTransformer(method="yeo-johnson")),
            ("scale", StandardScaler()),
        ]
    )
    transformed_features = preprocessor.fit_transform(features)
    model = KMeans(n_clusters=3, n_init=50, random_state=42)
    labels = model.fit_predict(transformed_features)
    hierarchical_labels = AgglomerativeClustering(
        n_clusters=3,
        linkage="ward",
    ).fit_predict(transformed_features)
    sample_silhouettes = silhouette_samples(transformed_features, labels)
    evaluation = {
        "Silhouette (global)": silhouette_score(transformed_features, labels),
        "Davies-Bouldin": davies_bouldin_score(transformed_features, labels),
        "Calinski-Harabasz": calinski_harabasz_score(transformed_features, labels),
        "Adjusted Rand Index vs. hierarchical": adjusted_rand_score(
            labels,
            hierarchical_labels,
        ),
    }
    clustered_data = training_data.copy()
    clustered_data[CLUSTER_FEATURES] = features
    clustered_data["cluster"] = labels
    clustered_data["silhouette"] = sample_silhouettes
    cluster_silhouettes = (
        clustered_data.groupby("cluster")["silhouette"]
        .mean()
        .rename("Silhouette rata-rata")
    )
    return (
        preprocessor,
        model,
        features,
        clustered_data,
        evaluation,
        cluster_silhouettes,
    )


def predict_cluster(raw_input, clustering_result):
    preprocessor, model, training_features = clustering_result[:3]
    input_features = build_cluster_features(pd.DataFrame([raw_input]))
    predicted_cluster = int(
        model.predict(preprocessor.transform(input_features))[0]
    )
    outside_training_range = [
        feature
        for feature in CLUSTER_FEATURES
        if input_features.iloc[0][feature] < training_features[feature].min()
        or input_features.iloc[0][feature] > training_features[feature].max()
    ]
    return predicted_cluster, input_features, outside_training_range
