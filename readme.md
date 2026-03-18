# Proyek Analisis Data: E-Commerce Public Dataset
## Dashboard Interaktif

### Cara Menjalankan Dashboard Secara Lokal

Ikuti langkah-langkah berikut untuk menjalankan dashboard di komputer Anda:

#### 1. **Clone Repository**
```bash
git clone https://github.com/username/nama-repository-anda.git
cd nama-repository-anda
```

#### 2. **Buat dan Aktifkan Virtual Environment**
**Untuk Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Untuk Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. **Instal Dependensi**
Pastikan Anda memiliki file `requirements.txt` yang berisi semua library yang diperlukan. Jika belum, buat dengan isi:
```
pandas
numpy
matplotlib
seaborn
streamlit
folium
geopandas
```

Kemudian jalankan:
```bash
pip install -r requirements.txt
```

#### 4. **Jalankan Aplikasi Streamlit**
```bash
streamlit run dashboard.py
```

#### 5. **Akses Dashboard**
Setelah perintah di atas dijalankan, Anda akan melihat output seperti:
```
Local URL: http://localhost:8501    
Network URL: http://172.16.11.233:8501
```
Buka browser dan akses `http://localhost:8501` untuk melihat dashboard.