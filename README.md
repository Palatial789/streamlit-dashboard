# Dashboard Performa Media Sosial

Dashboard Streamlit ini memiliki dua halaman:

- **Dashboard performa** untuk melihat engagement rate, impression bulanan, dan ringkasan performa per tahun dari `data/bsd_2023_2025.csv`. Bulan ditampilkan dari Januari sampai Desember, dengan angka bulanan dan rentang minimum–maksimum. Skala impression pada chart menggunakan pemisah ribuan titik.
- **Clustering engagement** yang menerapkan pipeline dari notebook: enam fitur rasio, PowerTransformer Yeo-Johnson, StandardScaler, lalu K-Means dengan 3 cluster, `n_init=50`, dan `random_state=42`. Halaman menampilkan korelasi fitur, skewness setelah transformasi, evaluasi kandidat `k=2–10` dengan minimum 4 bulan per cluster, metrik evaluasi akhir, perbandingan ARI dengan Agglomerative Clustering, silhouette per cluster, serta scatterplot yang dapat dipilih sumbunya. Pengguna dapat memasukkan metrik bulanan untuk prediksi cluster.

Engagement rate dihitung sebagai total like, komentar, share, dan save dibagi total impression.

### How to run it on your own machine

1. Install the requirements

   ```
   pip install -r requirements.txt
   ```

2. Run the app

   ```
   streamlit run streamlit_app.py
   ```
