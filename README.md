# Dashboard Performa Media Sosial

Dashboard Streamlit ini menggunakan struktur MVC sederhana dan memiliki dua halaman:

- **Dashboard performa** untuk melihat engagement rate, impression bulanan, dan ringkasan performa per tahun dari `data/bsd_2023_2025.csv`.
- **Clustering engagement** dengan enam fitur rasio, PowerTransformer Yeo-Johnson, StandardScaler, K-Means (3 cluster), evaluasi model, profil cluster, scatterplot interaktif, dan prediksi dari metrik yang dimasukkan pengguna.

Engagement rate dihitung sebagai total like, komentar, share, dan save dibagi total impression.

### Struktur MVC

- `model.py` memuat data, menghitung fitur, melatih model, dan menghasilkan prediksi.
- `view.py` berisi komponen tampilan, grafik, tabel, dan input Streamlit.
- `controller.py` mengatur navigasi serta menghubungkan tampilan dengan model.
- `streamlit_app.py` menjadi entry point untuk menjalankan aplikasi.

### How to run it on your own machine

1. Install the requirements

   ```
   pip install -r requirements.txt
   ```

2. Run the app

   ```
   streamlit run streamlit_app.py
   ```
