# E-Commerce Public Dataset Dashboard ✨

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

## Project Overview
Proyek ini bertujuan untuk menganalisis performa penjualan pada dataset E-Commerce, termasuk:
- Performa kategori produk
- Tren penjualan dari waktu ke waktu
- Kontribusi wilayah terhadap revenue
- Segmentasi pelanggan menggunakan RFM Analysis

## Business Questions
1. Kategori produk apa yang memiliki performa terbaik dan terendah?
2. Bagaimana tren penjualan dari waktu ke waktu?
3. Wilayah mana yang paling berkontribusi terhadap revenue?

## Insight
- Beberapa kategori produk mendominasi revenue secara signifikan
- Tren penjualan mengalami peningkatan hingga periode tertentu
- Wilayah SP memberikan kontribusi terbesar terhadap total revenue
- Mayoritas pelanggan termasuk dalam kategori low value customer berdasarkan analisis RFM

## Author
Almas Ikramina
Submission Dicoding - Belajar Fundamental Analisis Data
