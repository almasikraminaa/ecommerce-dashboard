# E-Commerce Public Dataset Dashboard ✨

## Project Overview
Proyek ini bertujuan untuk melakukan analisis data secara menyeluruh pada E-Commerce Public Dataset guna menghasilkan insight yang relevan bagi kebutuhan bisnis.

Analisis yang dilakukan mencakup:

- 📈 Analisis tren penjualan dari waktu ke waktu
- 📦 Evaluasi performa kategori produk
- 🌍 Analisis kontribusi wilayah terhadap revenue
- 👥 Segmentasi pelanggan menggunakan RFM Analysis (Recency, Frequency, Monetary)

Hasil analisis divisualisasikan dalam bentuk dashboard interaktif menggunakan Streamlit, yang dilengkapi filter rentang waktu dan wilayah (state).

## Business Questions
1. Kategori produk apa yang memiliki performa terbaik dan terendah berdasarkan jumlah item terjual dan total revenue pada periode 2016–2018?
2. Bagaimana tren penjualan (jumlah order dan revenue) dari waktu ke waktu selama periode 2016–2018?
3. Wilayah (state) mana yang memberikan kontribusi terbesar terhadap total transaksi dan revenue pada periode 2016–2018?

## Insight
📈 Tren Penjualan
- Tren penjualan menunjukkan peningkatan dari tahun 2016 hingga 2018, meskipun terdapat fluktuasi di beberapa periode.
- Kenaikan jumlah order sejalan dengan peningkatan revenue, menunjukkan pertumbuhan permintaan yang konsisten.

📦 Performa Kategori Produk
- Hanya beberapa kategori produk yang mendominasi revenue secara signifikan.
- Terdapat perbedaan yang jelas antara kategori dengan performa tinggi dan rendah, menunjukkan adanya konsentrasi penjualan pada kategori tertentu.

🌍 Kontribusi Wilayah
- State SP (São Paulo) menjadi kontributor terbesar terhadap jumlah transaksi dan revenue.
- State lain seperti RJ dan MG juga berkontribusi, namun masih jauh di bawah SP.
- Hal ini menunjukkan adanya ketimpangan distribusi transaksi antar wilayah.

👥 Segmentasi Pelanggan (RFM)
- Mayoritas pelanggan termasuk dalam kategori Low Value dan Medium Value Customer.
- Sebagian kecil pelanggan termasuk High Value Customer, namun memberikan kontribusi besar terhadap revenue.
- Hal ini menunjukkan peluang untuk meningkatkan engagement pelanggan bernilai rendah dan memaksimalkan loyalitas pelanggan bernilai tinggi

🔍 Insight Distribusi Data (EDA)
- Distribusi payment_value sangat right-skewed, di mana sebagian besar transaksi bernilai kecil.
- Terdapat banyak outlier dengan nilai transaksi tinggi, yang berkontribusi besar terhadap total revenue.
Terdapat hubungan positif antara price dan payment_value, namun dengan variasi yang menunjukkan adanya faktor lain (seperti jumlah item atau biaya tambahan).

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App
```
cd dashboard
streamlit run dashboard.py
```

## Author
Almas Ikramina
Submission Dicoding - Belajar Fundamental Analisis Data
