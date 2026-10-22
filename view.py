import altair as alt
import pandas as pd
import streamlit as st
from model import CLUSTER_FEATURES, MONTH_NAMES


def render_app_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #f6f8fc 0%, #ffffff 340px);
        }
        .block-container {
            max-width: 1440px;
            padding-top: 2.2rem;
            padding-bottom: 3rem;
        }
        [data-testid="stSidebar"] {
            background: #111827;
        }
        [data-testid="stSidebar"] * {
            color: #f9fafb;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            border-radius: 10px;
            padding: 0.35rem 0.5rem;
        }
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e6eaf0;
            border-radius: 14px;
            padding: 1rem 1.1rem;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
        }
        [data-testid="stMetricLabel"] {
            color: #64748b;
        }
        h1, h2, h3 {
            letter-spacing: -0.025em;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #e6eaf0;
            border-radius: 12px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title, subtitle):
    st.title(title)
    st.caption(subtitle)


def render_performance_dashboard(data):
    years = sorted(data["year"].dropna().astype(int).unique())
    selected_year = st.selectbox("Pilih tahun", years, index=len(years) - 1)
    year_data = data[data["year"] == selected_year].sort_values("month_num").copy()
    year_data["Bulan"] = pd.Categorical(
        year_data["Bulan"],
        categories=MONTH_NAMES,
        ordered=True,
    )

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
    impression_chart = (
        alt.Chart(year_data)
        .mark_bar()
        .encode(
            x=alt.X("Bulan:N", sort=MONTH_NAMES, title="Bulan"),
            y=alt.Y(
                "Total Impressions:Q",
                title="Total impression",
                axis=alt.Axis(
                    labelExpr="replace(format(datum.value, ',.0f'), /,/g, '.')"
                ),
            ),
            tooltip=[
                alt.Tooltip("Bulan:N", title="Bulan"),
                alt.Tooltip("Total Impressions:Q", title="Impression", format=","),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(impression_chart, width="stretch")

    st.header("Engagement rate bulanan")
    engagement_chart = (
        alt.Chart(year_data)
        .mark_line(point=True)
        .encode(
            x=alt.X("Bulan:N", sort=MONTH_NAMES, title="Bulan"),
            y=alt.Y(
                "Engagement Rate:Q",
                title="Engagement rate (%)",
                axis=alt.Axis(format=".2f"),
            ),
            tooltip=[
                alt.Tooltip("Bulan:N", title="Bulan"),
                alt.Tooltip("Engagement Rate:Q", title="Engagement rate", format=".2f"),
            ],
        )
        .properties(height=280)
    )
    st.altair_chart(engagement_chart, width="stretch")
    st.caption(
        f"Rentang {selected_year}: impression "
        f"{year_data['Total Impressions'].min():,.0f}–"
        f"{year_data['Total Impressions'].max():,.0f}; engagement rate "
        f"{year_data['Engagement Rate'].min():.2f}%–"
        f"{year_data['Engagement Rate'].max():.2f}%."
    )
    st.subheader("Angka per bulan")
    st.dataframe(
        year_data[["Bulan", "Total Impressions", "Engagement Rate"]].rename(
            columns={
                "Bulan": "Bulan",
                "Total Impressions": "Impression",
                "Engagement Rate": "Engagement rate (%)",
            }
        ),
        hide_index=True,
        width="stretch",
        column_config={
            "Impression": st.column_config.NumberColumn(format="%d"),
            "Engagement rate (%)": st.column_config.NumberColumn(format="%.2f"),
        },
    )

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
            annual_summary.rename(
                columns={"year": "Tahun", "Follower_baru": "Follower baru"}
            ),
            hide_index=True,
            width="stretch",
            column_config={
                "Tahun": st.column_config.NumberColumn(format="%d"),
                "Impression": st.column_config.NumberColumn(format="%d"),
                "Interaksi": st.column_config.NumberColumn(format="%d"),
                "Post": st.column_config.NumberColumn(format="%d"),
                "Follower baru": st.column_config.NumberColumn(format="%d"),
                "Engagement Rate": st.column_config.NumberColumn(format="%.2f"),
            },
        )
    with summary_right:
        annual_chart = (
            alt.Chart(annual_summary)
            .mark_bar()
            .encode(
                x=alt.X("year:O", title="Tahun"),
                y=alt.Y(
                    "Impression:Q",
                    title="Total impression",
                    axis=alt.Axis(
                        labelExpr="replace(format(datum.value, ',.0f'), /,/g, '.')"
                    ),
                ),
                tooltip=[
                    alt.Tooltip("year:O", title="Tahun"),
                    alt.Tooltip("Impression:Q", title="Impression", format=",.0f"),
                ],
            )
            .properties(height=280)
        )
        st.altair_chart(annual_chart, width="stretch")


def render_clustering_dashboard(data, clustering_result, predict_cluster):
    (
        training_features,
        clustered_data,
        evaluation,
        cluster_silhouettes,
    ) = clustering_result[2:]

    st.title("Clustering engagement")
    st.caption(
        "Implementasi pipeline clustering dari notebook pada data bulanan "
        "2023–2025 yang tersedia di dashboard."
    )
    st.subheader("Model yang digunakan")
    st.write(
        "Fitur rasio engagement, share, save, profile visit, website tap, dan "
        "konversi follow ditransformasi dengan PowerTransformer "
        "(Yeo-Johnson), lalu distandardisasi. K-Means menggunakan 3 cluster, "
        "n_init=50, dan random_state=42. Hasil dibandingkan dengan "
        "Agglomerative Clustering linkage Ward."
    )

    evaluation_columns = st.columns(4)
    evaluation_columns[0].metric(
        "Silhouette (global)",
        f"{evaluation['Silhouette (global)']:.3f}",
    )
    evaluation_columns[1].metric(
        "Davies-Bouldin",
        f"{evaluation['Davies-Bouldin']:.3f}",
    )
    evaluation_columns[2].metric(
        "Calinski-Harabasz",
        f"{evaluation['Calinski-Harabasz']:.2f}",
    )
    evaluation_columns[3].metric(
        "ARI vs. hierarchical",
        f"{evaluation['Adjusted Rand Index vs. hierarchical']:.3f}",
    )
    st.caption(
        "Silhouette semakin tinggi dan Davies-Bouldin semakin rendah umumnya "
        "menunjukkan cluster yang lebih terpisah. ARI membandingkan label "
        "K-Means dengan Agglomerative Clustering."
    )

    # st.subheader("Seleksi jumlah cluster")
    # st.caption(
    #     "Kandidat k=2–10 dievaluasi seperti di notebook. Tabel kandidat yang "
    #     "memenuhi ukuran cluster minimum (4 bulan) diurutkan berdasarkan silhouette."
    # )
    # st.dataframe(
    #     eligible_k_evaluation.reset_index(),
    #     hide_index=True,
    #     width="stretch",
    #     column_config={
    #         "k": st.column_config.NumberColumn(format="%d"),
    #         "Inertia": st.column_config.NumberColumn(format="%.3f"),
    #         "Silhouette": st.column_config.NumberColumn(format="%.3f"),
    #         "Davies-Bouldin": st.column_config.NumberColumn(format="%.3f"),
    #         "Calinski-Harabasz": st.column_config.NumberColumn(format="%.2f"),
    #         "Ukuran cluster minimum": st.column_config.NumberColumn(format="%d"),
    #     },
    # )
    # st.caption("Nilai k final mengikuti notebook: 3.")

    # feature_bounds = pd.DataFrame({
    #     "Fitur": CLUSTER_FEATURES,
    #     "Minimum data": training_features.min().values,
    #     "Maksimum data": training_features.max().values,
    # })
    # st.subheader("Rentang fitur rasio pada data pelatihan")
    # st.dataframe(
    #     feature_bounds,
    #     hide_index=True,
    #     width="stretch",
    #     column_config={
    #         "Minimum data": st.column_config.NumberColumn(format="%.6f"),
    #         "Maksimum data": st.column_config.NumberColumn(format="%.6f"),
    #     },
    # )
    # st.subheader("Korelasi kandidat fitur")
    # correlation_values = training_features.corr().rename_axis("Fitur X").reset_index()
    # correlation_data = correlation_values.melt(
    #     id_vars="Fitur X",
    #     var_name="Fitur Y",
    #     value_name="Korelasi",
    # )
    # correlation_chart = (
    #     alt.Chart(correlation_data)
    #     .mark_rect()
    #     .encode(
    #         x=alt.X("Fitur X:N", sort=CLUSTER_FEATURES, title=None),
    #         y=alt.Y("Fitur Y:N", sort=CLUSTER_FEATURES, title=None),
    #         color=alt.Color(
    #             "Korelasi:Q",
    #             scale=alt.Scale(scheme="redblue", domain=[-1, 1]),
    #             title="Korelasi",
    #         ),
    #         tooltip=[
    #             alt.Tooltip("Fitur X:N"),
    #             alt.Tooltip("Fitur Y:N"),
    #             alt.Tooltip("Korelasi:Q", format=".2f"),
    #         ],
    #     )
    # )
    # correlation_labels = (
    #     alt.Chart(correlation_data)
    #     .mark_text()
    #     .encode(
    #         x=alt.X("Fitur X:N", sort=CLUSTER_FEATURES),
    #         y=alt.Y("Fitur Y:N", sort=CLUSTER_FEATURES),
    #         text=alt.Text("Korelasi:Q", format=".2f"),
    #         color=alt.condition(
    #             "abs(datum.Korelasi) > 0.5",
    #             alt.value("white"),
    #             alt.value("black"),
    #         ),
    #     )
    # )
    # st.altair_chart(
    #     (correlation_chart + correlation_labels).properties(height=320),
    #     width="stretch",
    # )
    # st.subheader("Skewness setelah transformasi")
    # st.dataframe(
    #     transformed_skewness.rename("Skewness").rename_axis("Fitur").reset_index(),
    #     hide_index=True,
    #     width="stretch",
    #     column_config={
    #         "Skewness": st.column_config.NumberColumn(format="%.3f"),
    #     },
    # )

    st.subheader("Masukkan metrik bulanan")
    st.caption(
        "Masukkan angka total untuk satu bulan. Fitur rasio dihitung otomatis "
        "mengikuti rumus dari notebook."
    )
    median_inputs = data[
        [
            "Total Post",
            "Total Impressions",
            "Like",
            "Comment",
            "Share",
            "Save",
            "Profile Visits",
            "Website Taps",
            "Follows",
        ]
    ].median()
    input_columns = st.columns(3)
    raw_input = {}
    input_fields = [
        ("Total Post", "Total post", 1),
        ("Total Impressions", "Total impression", 1),
        ("Like", "Like", 0),
        ("Comment", "Comment", 0),
        ("Share", "Share", 0),
        ("Save", "Save", 0),
        ("Profile Visits", "Profile visits", 1),
        ("Website Taps", "Website taps", 0),
        ("Follows", "Follows", 0),
    ]
    for index, (column, label, minimum) in enumerate(input_fields):
        with input_columns[index % len(input_columns)]:
            raw_input[column] = st.number_input(
                label,
                min_value=minimum,
                value=max(minimum, int(round(median_inputs[column]))),
                step=1,
                key=f"cluster_input_{column}",
            )

    predicted_cluster, input_features, outside_training_range = predict_cluster(
        raw_input
    )
    st.success(f"Input ini diprediksi masuk **Cluster {predicted_cluster}**.")

    if outside_training_range:
        st.warning(
            "Fitur "
            + ", ".join(outside_training_range)
            + " berada di luar rentang data pelatihan. Prediksi tetap dihitung, "
            "tetapi hasilnya dapat kurang representatif."
        )

    st.subheader("Ringkasan kualitas tiap cluster")
    silhouette_summary = cluster_silhouettes.to_frame().reset_index()
    cluster_sizes = (
        clustered_data["cluster"]
        .value_counts()
        .sort_index()
        .rename("Jumlah bulan")
        .reset_index()
    )
    silhouette_summary = silhouette_summary.merge(cluster_sizes, on="cluster")
    st.dataframe(
        silhouette_summary.rename(
            columns={
                "cluster": "Cluster",
                "silhouette": "Silhouette rata-rata",
            }
        ),
        hide_index=True,
        width="stretch",
        column_config={
            "Silhouette rata-rata": st.column_config.NumberColumn(format="%.3f"),
            "Jumlah bulan": st.column_config.NumberColumn(format="%d"),
        },
    )

    st.subheader("Profil fitur per cluster")
    cluster_profile = training_features.assign(
        Cluster=clustered_data["cluster"].values
    ).groupby("Cluster", as_index=False)[CLUSTER_FEATURES].mean()
    feature_descriptions = {
        "Engagement_Rate": "engagement",
        "Share_Rate": "share",
        "Save_Rate": "save",
        "Profile_Visit_Rate": "kunjungan profil",
        "Website_Tap_Rate": "ketukan website",
        "Follow_Conversion_Rate": "konversi kunjungan profil menjadi follow",
    }
    st.dataframe(
        cluster_profile,
        hide_index=True,
        width="stretch",
        column_config={
            **{
                feature: st.column_config.NumberColumn(format="%.6f")
                for feature in CLUSTER_FEATURES
            },
        },
    )
    st.caption(
        "Semua nilai profil adalah rata-rata rasio dalam cluster. Cluster 0, 1, "
        "dan 2 hanya label kelompok, bukan urutan kualitas atau performa."
    )

    st.subheader("Penjelasan karakteristik cluster")
    st.write(
        "Setiap cluster mengelompokkan bulan dengan pola enam rasio yang "
        "serupa. Ciri berikut menunjukkan rasio yang paling berbeda dari "
        "rata-rata seluruh bulan; rasio yang lebih tinggi tidak selalu berarti "
        "performa keseluruhan lebih baik."
    )
    overall_feature_means = training_features[CLUSTER_FEATURES].mean()
    overall_feature_stds = training_features[CLUSTER_FEATURES].std(ddof=0)
    for _, profile in cluster_profile.iterrows():
        differences = []
        for feature in CLUSTER_FEATURES:
            feature_std = overall_feature_stds[feature]
            if feature_std == 0:
                continue
            standardized_difference = (
                profile[feature] - overall_feature_means[feature]
            ) / feature_std
            differences.append(
                (abs(standardized_difference), standardized_difference, feature)
            )
        differences.sort(reverse=True)
        notable_differences = [
            item for item in differences[:2] if item[0] >= 0.25
        ]
        if notable_differences:
            characteristics = "; ".join(
                f"{feature_descriptions[feature]} "
                f"{'lebih tinggi' if difference > 0 else 'lebih rendah'} "
                f"({profile[feature] * 100:.2f}%)"
                for _, difference, feature in notable_differences
            )
            st.markdown(f"**Cluster {int(profile['Cluster'])}:** {characteristics}.")
        else:
            st.markdown(
                f"**Cluster {int(profile['Cluster'])}:** tidak ada rasio yang "
                "tampak menonjol dibanding rata-rata seluruh bulan."
            )

    st.subheader("Scatterplot hasil clustering")
    axis_columns = st.columns(2)
    x_feature = axis_columns[0].selectbox(
        "Sumbu X",
        CLUSTER_FEATURES,
        index=0,
        key="cluster_x_feature",
    )
    y_feature = axis_columns[1].selectbox(
        "Sumbu Y",
        CLUSTER_FEATURES,
        index=3,
        key="cluster_y_feature",
    )
    scatter_data = clustered_data.copy()
    scatter_data["year"] = scatter_data["year"].astype(str)
    scatter_data["Jenis"] = "Data historis"
    scatter_data["Cluster"] = scatter_data["cluster"].astype(str)
    scatter_data["X"] = scatter_data[x_feature] * 100
    scatter_data["Y"] = scatter_data[y_feature] * 100
    user_point = pd.DataFrame(
        [
            {
                "Bulan": "Input pengguna",
                "year": "Input",
                "cluster": predicted_cluster,
                "Cluster": str(predicted_cluster),
                "Jenis": "Input pengguna",
                "X": input_features.iloc[0][x_feature] * 100,
                "Y": input_features.iloc[0][y_feature] * 100,
            }
        ]
    )
    scatter_data = pd.concat([scatter_data, user_point], ignore_index=True)
    historical_points = (
        alt.Chart(scatter_data)
        .transform_filter(alt.datum.Jenis == "Data historis")
        .mark_circle(size=90, opacity=0.8)
        .encode(
            x=alt.X("X:Q", title=f"{x_feature} (%)", axis=alt.Axis(format=".3f")),
            y=alt.Y("Y:Q", title=f"{y_feature} (%)", axis=alt.Axis(format=".3f")),
            color=alt.Color("Cluster:N", title="Cluster"),
            tooltip=[
                alt.Tooltip("year:N", title="Tahun"),
                alt.Tooltip("Bulan:N", title="Bulan"),
                alt.Tooltip("Cluster:N", title="Cluster"),
                alt.Tooltip("X:Q", title=f"{x_feature} (%)", format=".4f"),
                alt.Tooltip("Y:Q", title=f"{y_feature} (%)", format=".4f"),
            ],
        )
    )
    input_point = (
        alt.Chart(scatter_data)
        .transform_filter(alt.datum.Jenis == "Input pengguna")
        .mark_point(shape="diamond", size=220, filled=True, color="#111111")
        .encode(
            x="X:Q",
            y="Y:Q",
            tooltip=[
                alt.Tooltip("Jenis:N", title="Jenis data"),
                alt.Tooltip("Cluster:N", title="Prediksi cluster"),
                alt.Tooltip("X:Q", title=f"{x_feature} (%)", format=".4f"),
                alt.Tooltip("Y:Q", title=f"{y_feature} (%)", format=".4f"),
            ],
        )
    )
    st.altair_chart(
        (historical_points + input_point).properties(height=400),
        width="stretch",
    )
    st.caption(
        "Lingkaran menunjukkan data historis, sedangkan berlian hitam menunjukkan "
        "input pengguna. Nilai rasio pada sumbu ditampilkan dalam persen."
    )
