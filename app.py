import streamlit as st
import pandas as pd
import pymupdf as fitz
from ai_engine import ekstrak_data_pdf
from calculator import hitung_valuasi

# ==========================================
# 1. KONFIGURASI HALAMAN & STYLE DASAR
# ==========================================
st.set_page_config(page_title="INTRINSIK.AI", page_icon="📈", layout="wide")

# Hanya menggunakan CSS minimalis untuk font dan tombol
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Tombol Utama */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    /* Judul */
    .header-title {
        font-size: 45px;
        font-weight: 800;
        color: #3B82F6; /* Biru modern */
        margin-bottom: 0px;
    }
    .header-subtitle {
        font-size: 18px;
        color: #6B7280;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-title">📈 INTRINSIK.AI</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Robo-Advisor Valuasi Fundamental & Analisis Investasi</div>', unsafe_allow_html=True)

# ==========================================
# 2. INISIALISASI SESSION STATE
# ==========================================
if 'analisis_selesai' not in st.session_state:
    st.session_state['analisis_selesai'] = False
if 'hitung_selesai' not in st.session_state:
    st.session_state['hitung_selesai'] = False

# ==========================================
# 3. SIDEBAR: INPUT DATA
# ==========================================
with st.sidebar:
    st.markdown("### 📥 Input Data")
    ticker = st.text_input("Kode Saham (Manual)", value="ICBP")
    harga_pasar = st.number_input("Harga Saham Pasar (Rp)", min_value=100, value=10000, step=100)
    
    st.divider()
    st.markdown("### 📄 Unggah Dokumen")
    uploaded_file = st.file_uploader("Upload Laporan Keuangan (PDF)", type=["pdf"])
    
    st.divider()
    demo_mode = st.toggle("🛠️ Demo Mode (Simulasi)")
    st.caption("Aktifkan jika internet/server error saat presentasi.")
    
    tombol_analisis = st.button("🚀 Mulai Analisis", use_container_width=True, type="primary")

# ==========================================
# 4. LOGIKA PROSES ANALISIS
# ==========================================
if tombol_analisis:
    if uploaded_file is None:
        st.toast("⚠️ Silakan unggah file PDF terlebih dahulu!", icon="⚠️")
    else:
        st.session_state['analisis_selesai'] = False
        st.session_state['hitung_selesai'] = False
        
        with st.spinner("AI Vision-Language Model sedang membaca dokumen..."):
            st.session_state['pdf_bytes'] = uploaded_file.getvalue()
            hasil_ai = ekstrak_data_pdf(uploaded_file, is_demo=demo_mode)
            
            if hasil_ai["status"] in ["invalid", "error"]:
                st.error(hasil_ai["pesan"])
            else:
                st.session_state['data_keuangan'] = hasil_ai["data"]
                st.session_state['analisis_selesai'] = True

# ==========================================
# 5. TAMPILAN VERIFIKASI (HITL) 
# ==========================================
if st.session_state['analisis_selesai']:
    data_keuangan = st.session_state['data_keuangan']
    
    st.markdown("### 🔍 Verifikasi Data Ekstraksi AI")
    st.info(f"**Periode Laporan Terdeteksi AI:** {data_keuangan.get('periode_laporan', '-')}")
    
    # Layout Kiri Kanan
    col_gambar, col_form = st.columns([1, 1], gap="large")
    
    # --- KIRI: PDF PREVIEW ---
    with col_gambar:
        with st.container(border=True):
            st.markdown("#### 📄 Pratinjau Halaman PDF")
            metrik_pilihan = st.selectbox(
                "Pilih data untuk melihat sumber halamannya:",
                ["Laba Bersih", "Total Ekuitas", "Total Pendapatan", "Total Liabilitas", "Arus Kas", "Jumlah Saham"]
            )
            
            if metrik_pilihan == "Laba Bersih": hal_target = data_keuangan.get('hal_laba', 1)
            elif metrik_pilihan == "Total Ekuitas": hal_target = data_keuangan.get('hal_ekuitas', 1)
            elif metrik_pilihan == "Total Pendapatan": hal_target = data_keuangan.get('hal_pendapatan', 1)
            elif metrik_pilihan == "Total Liabilitas": hal_target = data_keuangan.get('hal_liabilitas', 1)
            elif metrik_pilihan == "Arus Kas": hal_target = data_keuangan.get('hal_arus_kas', 1)
            else: hal_target = data_keuangan.get('hal_saham', 1)

            try:
                pdf_document = fitz.open(stream=st.session_state['pdf_bytes'], filetype="pdf")
                page = pdf_document.load_page(hal_target - 1) 
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                st.image(pix.tobytes("png"), caption=f"Halaman {hal_target}", use_container_width=True)
            except Exception as e:
                st.error(f"Gagal memuat pratinjau: {e}")

    # --- KANAN: FORM HITL ---
    with col_form:
        with st.container(border=True):
            st.markdown("#### 📝 Form Verifikasi (HITL)")
            with st.form("form_hitl"):
                laba_bersih = st.number_input("Laba Bersih (Juta Rp)", value=int(data_keuangan['laba_bersih_juta']))
                ekuitas = st.number_input("Total Ekuitas (Juta Rp)", value=int(data_keuangan['total_ekuitas_juta']))
                pendapatan = st.number_input("Total Pendapatan (Juta Rp)", value=int(data_keuangan.get('total_pendapatan_juta', 0)))
                liabilitas = st.number_input("Total Liabilitas (Juta Rp)", value=int(data_keuangan.get('total_liabilitas_juta', 0)))
                net_cfo = st.number_input("Net CFO (Juta Rp)", value=int(data_keuangan['net_cfo_juta']))
                net_cfi = st.number_input("Net CFI (Juta Rp)", value=int(data_keuangan['net_cfi_juta']))
                net_cff = st.number_input("Net CFF (Juta Rp)", value=int(data_keuangan['net_cff_juta']))
                saham = st.number_input("Jumlah Saham Beredar", value=int(data_keuangan['jumlah_saham']))
                
                submit_hitl = st.form_submit_button("✅ Data Sudah Benar, Hitung Valuasi!", use_container_width=True, type="primary")
                
    if submit_hitl:
        data_final = {
            "laba_bersih_juta": laba_bersih, "total_ekuitas_juta": ekuitas,
            "total_pendapatan_juta": pendapatan, "total_liabilitas_juta": liabilitas,
            "net_cfo_juta": net_cfo, "net_cfi_juta": net_cfi, "net_cff_juta": net_cff, 
            "jumlah_saham": saham,
            "total_kas_juta": data_keuangan.get('total_kas_juta', 0),
            "laba_ditahan_juta": data_keuangan.get('laba_ditahan_juta', 0)
        }
        st.session_state['hasil'] = hitung_valuasi(data_final, harga_pasar)
        st.session_state['hitung_selesai'] = True

# ==========================================
# 6. DASHBOARD HASIL AKHIR (LAYOUT BARU)
# ==========================================
if st.session_state['hitung_selesai']:
    hasil = st.session_state['hasil']
    data_keuangan = st.session_state['data_keuangan']
    
    st.divider()
    
    # --- BARIS 1: METRIK UTAMA (KOTAK BESAR) ---
    st.markdown("### 📊 Ringkasan Hasil")
    
    # Menentukan status
    is_undervalued = harga_pasar < hasil['nilai_intrinsik']
    
    # 3 Kolom untuk Metric Card
    m1, m2, m3 = st.columns(3)
    m1.metric("Harga Pasar Saat Ini", f"Rp {harga_pasar:,.0f}")
    m2.metric("Nilai Intrinsik (DCF)", f"Rp {hasil['nilai_intrinsik']:,.2f}")
    
    if is_undervalued:
        m3.metric("Status Valuasi", "UNDERVALUED", f"+{hasil['mos']:.2f}% Upside", delta_color="normal")
    else:
        m3.metric("Status Valuasi", "OVERVALUED", f"{hasil['mos']:.2f}% Downside", delta_color="inverse")
    
    st.divider()

    # --- BARIS 2: TAB DETAIL ---
    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Info Perusahaan", "⚖️ Valuasi Relatif", "💰 Valuasi DCF", "🩺 Kesehatan"])
    
    with tab1:
        st.markdown("#### Informasi Perusahaan")
        info_data = pd.DataFrame({
            "Keterangan": ["Nama Perusahaan", "Kode Saham", "Periode Laporan", "Harga Saham", "Jumlah Saham Beredar", "Market Cap (Kapitalisasi Pasar)"],
            "Nilai": [
                data_keuangan.get('nama_perusahaan', '-'), ticker, data_keuangan.get('periode_laporan', '-'),
                f"Rp {harga_pasar:,.0f}", f"{int(data_keuangan['jumlah_saham']):,}", f"Rp {hasil['market_cap']:,.0f}"
            ]
        })
        st.dataframe(info_data, use_container_width=True, hide_index=True)
        
    with tab2:
        st.markdown("#### Valuasi Relatif (Perbandingan Harga dengan Kinerja)")
        
        # Helper function untuk status
        def stat(cond, good, bad): return good if cond else bad

        rel_data = pd.DataFrame({
            "Metrik / Rasio": ["EPS", "PER", "BVPS", "PBV", "PSR", "CPS", "PCS", "REPS", "PRER"],
            "Nilai": [
                f"Rp {hasil['eps']:,.2f}", f"{hasil['per']:,.2f} x", 
                f"Rp {hasil['bvps']:,.2f}", f"{hasil['pbv']:,.2f} x", 
                f"{hasil['psr']:,.2f} x", f"Rp {hasil['cps']:,.2f}", f"{hasil['pcs']:,.2f} x", 
                f"Rp {hasil['reps']:,.2f}", f"{hasil['prer']:,.2f} x"
            ],
            "Keterangan": [
                stat(hasil['eps']>0, "🟢 Laba Positif", "🔴 Laba Negatif"),
                stat(hasil['per']<10, "🟢 Murah", ("🟡 Wajar" if hasil['per']<=20 else "🔴 Mahal")),
                stat(hasil['bvps']>harga_pasar, "🟢 Di atas Harga Pasar", "🟡 Di bawah Harga Pasar"),
                stat(hasil['pbv']<1.0, "🟢 Murah", ("🟡 Wajar" if hasil['pbv']<=2.5 else "🔴 Mahal")),
                stat(hasil['psr']<1.5, "🟢 Murah", ("🟡 Wajar" if hasil['psr']<=3.0 else "🔴 Mahal")),
                stat(hasil['cps']>(harga_pasar*0.1), "🟢 Kas Kuat", "🟡 Kas Terbatas"),
                stat(hasil['pcs']<5, "🟢 Murah", ("🟡 Wajar" if hasil['pcs']<=15 else "🔴 Mahal")),
                stat(hasil['reps']>0, "🟢 Laba Ditahan Positif", "🔴 Laba Ditahan Negatif"),
                stat(hasil['prer']<3.0, "🟢 Murah", ("🟡 Wajar" if hasil['prer']<=8.0 else "🔴 Mahal"))
            ]
        })
        st.dataframe(rel_data, use_container_width=True, hide_index=True)
        
    with tab3:
        st.markdown("#### Valuasi Absolut (Discounted Cash Flow)")
        st.write("Asumsi: Discount Rate = 11% | Perpetual Growth = 3% | Proyeksi = 10 Tahun")
        
        # Tabel Proyeksi
        dcf_df = pd.DataFrame({
            "Tahun Ke-": range(1, 11),
            "Proyeksi Laba (Juta Rp)": [f"{x:,.2f}" for x in hasil['projected_income']],
            "Nilai Sekarang / PV (Juta Rp)": [f"{x:,.2f}" for x in hasil['discounted_income']]
        })
        st.dataframe(dcf_df, use_container_width=True, hide_index=True)
        
        # Ringkasan Perhitungan (pakai st.metric atau tabel kecil)
        st.markdown("**Ringkasan Kalkulasi:**")
        col_a, col_b = st.columns(2)
        col_a.info(f"**Total PV Laba (10 Thn):**\nRp {hasil['total_pv']:,.2f} Juta")
        col_b.info(f"**Terminal Value Discounted:**\nRp {hasil['discounted_tv']:,.2f} Juta")
        
        st.success(f"**TOTAL VALUASI (Equity Value):** Rp {hasil['total_valuasi_juta']:,.2f} Juta")

    with tab4:
        st.markdown("#### Skrining Kesehatan Perusahaan")
        
        cfo_ok = data_keuangan['net_cfo_juta'] > 0
        cfi_ok = data_keuangan['net_cfi_juta'] < 0
        cff_ok = data_keuangan['net_cff_juta'] < 0
        
        sehat_data = pd.DataFrame({
            "Indikator": ["Arus Kas Operasi (CFO)", "Arus Kas Investasi (CFI)", "Arus Kas Pendanaan (CFF)", "ROE (Return on Equity)", "DER (Debt to Equity)", "NPM (Net Profit Margin)"],
            "Nilai": [
                f"Rp {data_keuangan['net_cfo_juta']:,.0f} Juta", f"Rp {data_keuangan['net_cfi_juta']:,.0f} Juta", f"Rp {data_keuangan['net_cff_juta']:,.0f} Juta",
                f"{hasil['roe']:.2f} %", f"{hasil['der']:.2f} x", f"{hasil['npm']:.2f} %"
            ],
            "Status": [
                "🟢 Sehat" if cfo_ok else "🔴 Waspada",
                "🟢 Ekspansi" if cfi_ok else "🟡 Waspada",
                "🟢 Bayar Utang/Dividen" if cff_ok else "🟡 Cari Utang",
                "🟢 Sangat Bagus" if hasil['roe'] > 15 else ("🟡 Wajar" if hasil['roe'] >= 5 else "🔴 Kurang"),
                "🟢 Aman" if hasil['der'] < 1.0 else ("🟡 Wajar" if hasil['der'] <= 2.0 else "🔴 Berisiko"),
                "🟢 Sangat Bagus" if hasil['npm'] > 15 else ("🟡 Wajar" if hasil['npm'] >= 5 else "🔴 Kurang")
            ]
        })
        st.dataframe(sehat_data, use_container_width=True, hide_index=True)