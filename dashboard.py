import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# KONFIGURASI untuk HALAMAN
st.set_page_config(
    page_title="E-Commerce Dashboard",
    layout="wide"
)

# MEMUAT DATA 
@st.cache_data
def load_data():
    """Memuat dan menggabungkan dataset yang diperlukan"""
    # Load datasets
    df_customers = pd.read_csv('customers_dataset.csv')
    df_orders = pd.read_csv('orders_dataset.csv')
    df_order_items = pd.read_csv('order_items_dataset.csv')
    df_products = pd.read_csv('products_dataset.csv')
    df_category_translation = pd.read_csv('product_category_name_translation.csv')
    
    # Convert datetime
    df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])
    
    # Merge datasets
    orders_customers = pd.merge(df_orders, df_customers, on='customer_id', how='left')
    orders_items = pd.merge(orders_customers, df_order_items, on='order_id', how='left')
    df_merged = pd.merge(orders_items, df_products, on='product_id', how='left')
    df_merged = pd.merge(df_merged, df_category_translation, on='product_category_name', how='left')
    
    # Create additional columns
    df_merged['order_month'] = df_merged['order_purchase_timestamp'].dt.to_period('M')
    df_merged['order_month_str'] = df_merged['order_month'].astype(str)
    df_merged['order_year'] = df_merged['order_purchase_timestamp'].dt.year
    df_merged['order_month_num'] = df_merged['order_purchase_timestamp'].dt.month
    df_merged['total_value'] = df_merged['price'] + df_merged['freight_value']
    
    return df_merged

# Load data
with st.spinner('Memuat data...'):
    df = load_data()

# Bagian SIDEBAR 
st.sidebar.title(" E-Commerce Dashboard")
st.sidebar.markdown("---")

# Filter Tahun
available_years = sorted(df['order_year'].dropna().unique())
selected_years = st.sidebar.multiselect(
    "Pilih Tahun",
    available_years,
    default=available_years
)

# Filter Kategori Produk (Top 10)
top_categories = df['product_category_name_english'].value_counts().head(10).index.tolist()
selected_categories = st.sidebar.multiselect(
    "Pilih Kategori Produk",
    top_categories,
    default=top_categories[:5]
)

# Filter Negara Bagian
top_states = df['customer_state'].value_counts().head(10).index.tolist()
selected_states = st.sidebar.multiselect(
    "Pilih Negara Bagian",
    top_states,
    default=top_states[:5]
)

# Filter data berdasarkan input
filtered_df = df[
    (df['order_year'].isin(selected_years)) &
    (df['product_category_name_english'].isin(selected_categories)) &
    (df['customer_state'].isin(selected_states))
]

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Dashboard ini menampilkan analisis E-Commerce Public Dataset**
    - Bagaimana pola pembelian pelanggan berdasarkan kategori produk?
    - Bagaimana tren penjualan bulanan dan pengaruh lokasi geografis terhadap nilai transaksi?
    """
)

# MAIN DASHBOARD 
st.title("  Dashboard Analisis E-Commerce")
st.markdown("---")

# METRIK UTAMA
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = filtered_df['order_id'].nunique()
    st.metric("Total Orders", f"{total_orders:,}")

with col2:
    total_revenue = filtered_df['total_value'].sum()
    st.metric("Total Revenue", f"R$ {total_revenue:,.2f}")

with col3:
    avg_order_value = filtered_df.groupby('order_id')['total_value'].sum().mean()
    st.metric("Rata-rata Nilai Order", f"R$ {avg_order_value:,.2f}")

with col4:
    unique_customers = filtered_df['customer_unique_id'].nunique()
    st.metric("Jumlah Pelanggan", f"{unique_customers:,}")

st.markdown("---")

# PERTANYAAN 1: KATEGORI PRODUK 
st.header(" Pola Pembelian Berdasarkan Kategori Produk")

tab1, tab2, tab3 = st.tabs([" Penjualan per Kategori", " Revenue per Kategori", " Rata-rata Harga"])

# Hitung metrik per kategori
category_metrics = filtered_df.groupby('product_category_name_english').agg({
    'order_id': 'count',
    'total_value': 'sum',
    'price': 'mean'
}).round(2).sort_values('order_id', ascending=False).head(10)
category_metrics.columns = ['Jumlah Terjual', 'Total Revenue', 'Rata-rata Harga']

with tab1:
    fig1 = px.bar(
        category_metrics.reset_index(),
        x='product_category_name_english',
        y='Jumlah Terjual',
        title='Top 10 Kategori Produk Terlaris',
        labels={'product_category_name_english': 'Kategori', 'Jumlah Terjual': 'Jumlah Terjual (unit)'},
        color='Jumlah Terjual',
        color_continuous_scale='Blues'
    )
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = px.bar(
        category_metrics.reset_index().sort_values('Total Revenue', ascending=False).head(10),
        x='product_category_name_english',
        y='Total Revenue',
        title='Top 10 Kategori Berdasarkan Total Revenue',
        labels={'product_category_name_english': 'Kategori', 'Total Revenue': 'Total Revenue (R$)'},
        color='Total Revenue',
        color_continuous_scale='Greens'
    )
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig3 = px.bar(
        category_metrics.reset_index().sort_values('Rata-rata Harga', ascending=False).head(10),
        x='product_category_name_english',
        y='Rata-rata Harga',
        title='Top 10 Kategori dengan Rata-rata Harga Tertinggi',
        labels={'product_category_name_english': 'Kategori', 'Rata-rata Harga': 'Rata-rata Harga (R$)'},
        color='Rata-rata Harga',
        color_continuous_scale='Reds'
    )
    fig3.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

# Bubble chart
st.subheader(" Analisis Kategori: Jumlah Terjual vs Total Revenue")
fig_bubble = px.scatter(
    category_metrics.reset_index(),
    x='Jumlah Terjual',
    y='Total Revenue',
    size='Rata-rata Harga',
    color='product_category_name_english',
    hover_name='product_category_name_english',
    size_max=60,
    title='Ukuran bubble = Rata-rata Harga'
)
st.plotly_chart(fig_bubble, use_container_width=True)

# PERTANYAAN 2: TREN BULANAN DAN GEOGRAFIS 
st.header(" Tren Penjualan Bulanan & Pengaruh Lokasi")

# Tren bulanan
monthly_orders = filtered_df.groupby('order_month_str')['order_id'].nunique().reset_index()
monthly_orders.columns = ['bulan', 'jumlah_order']

monthly_revenue = filtered_df.groupby('order_month_str')['total_value'].sum().reset_index()
monthly_revenue.columns = ['bulan', 'total_revenue']

col5, col6 = st.columns(2)

with col5:
    fig4 = px.line(
        monthly_orders,
        x='bulan',
        y='jumlah_order',
        title='Tren Jumlah Order per Bulan',
        markers=True
    )
    fig4.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig4, use_container_width=True)

with col6:
    fig5 = px.line(
        monthly_revenue,
        x='bulan',
        y='total_revenue',
        title='Tren Total Revenue per Bulan',
        markers=True
    )
    fig5.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig5, use_container_width=True)

# Pola musiman
seasonal = filtered_df.groupby('order_month_num')['order_id'].nunique().reset_index()
nama_bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
              'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
seasonal['nama_bulan'] = nama_bulan

fig6 = px.bar(
    seasonal,
    x='nama_bulan',
    y='order_id',
    title='Rata-rata Jumlah Order per Bulan (Semua Tahun)',
    labels={'nama_bulan': 'Bulan', 'order_id': 'Jumlah Order'},
    color='order_id',
    color_continuous_scale='Viridis'
)
st.plotly_chart(fig6, use_container_width=True)

# Analisis per negara bagian
state_orders = filtered_df.groupby('customer_state')['order_id'].nunique().sort_values(ascending=False).head(10).reset_index()
state_orders.columns = ['state', 'jumlah_order']

state_revenue = filtered_df.groupby('customer_state')['total_value'].sum().sort_values(ascending=False).head(10).reset_index()
state_revenue.columns = ['state', 'total_revenue']

state_avg = filtered_df.groupby('customer_state')['total_value'].mean().sort_values(ascending=False).head(10).reset_index()
state_avg.columns = ['state', 'rata_rata_transaksi']

col7, col8 = st.columns(2)

with col7:
    fig7 = px.bar(
        state_orders,
        x='state',
        y='jumlah_order',
        title='Top 10 Negara Bagian - Jumlah Order',
        color='jumlah_order',
        color_continuous_scale='Oranges'
    )
    st.plotly_chart(fig7, use_container_width=True)

with col8:
    fig8 = px.bar(
        state_revenue,
        x='state',
        y='total_revenue',
        title='Top 10 Negara Bagian - Total Revenue',
        color='total_revenue',
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig8, use_container_width=True)

fig9 = px.bar(
    state_avg,
    x='state',
    y='rata_rata_transaksi',
    title='Top 10 Negara Bagian - Rata-rata Nilai Transaksi',
    color='rata_rata_transaksi',
    color_continuous_scale='Purples'
)
st.plotly_chart(fig9, use_container_width=True)

# ====================== ANALISIS LANJUTAN: RFM ======================
st.header(" Analisis Lanjutan: RFM Analysis")
st.markdown("""
**RFM Analysis** mengelompokkan pelanggan berdasarkan:
- **Recency**: Hari sejak terakhir transaksi
- **Frequency**: Jumlah transaksi
- **Monetary**: Total pengeluaran
""")

# Hitung RFM
reference_date = filtered_df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
rfm = filtered_df.groupby('customer_unique_id').agg({
    'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,
    'order_id': 'nunique',
    'total_value': 'sum'
}).reset_index()
rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']

# Buat skor
rfm['r_score'] = pd.qcut(rfm['recency'], 4, labels=[4, 3, 2, 1])
rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
rfm['m_score'] = pd.qcut(rfm['monetary'], 4, labels=[1, 2, 3, 4])
rfm['rfm_score'] = rfm['r_score'].astype(int) + rfm['f_score'].astype(int) + rfm['m_score'].astype(int)

def segmentasi(score):
    if score >= 10:
        return 'Champions'
    elif score >= 8:
        return 'Loyal Customers'
    elif score >= 6:
        return 'Potential Loyalists'
    elif score >= 4:
        return 'At Risk'
    else:
        return 'Lost'

rfm['segment'] = rfm['rfm_score'].apply(segmentasi)

# Visualisasi segmentasi
segment_counts = rfm['segment'].value_counts().reset_index()
segment_counts.columns = ['Segment', 'Jumlah']

fig10 = px.pie(
    segment_counts,
    values='Jumlah',
    names='Segment',
    title='Distribusi Segmen Pelanggan',
    color_discrete_sequence=px.colors.qualitative.Set3
)
st.plotly_chart(fig10, use_container_width=True)

# Tampilkan tabel RFM
st.subheader(" Data RFM (10 Sample)")
st.dataframe(rfm.head(10))

# ====================== FOOTER ======================
st.markdown("---")
st.markdown("Dashboard ini dibuat sebagai bagian dari Tugas Analisis Data - Nurul Amanda")