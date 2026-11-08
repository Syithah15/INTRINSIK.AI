import streamlit as st
import pandas as pd
import pymupdf as fitz
from ai_engine import ekstrak_data_pdf
from calculator import hitung_valuasi

# ==========================================
# 1. KONFIGURASI HALAMAN & CUSTOM CSS (TAMPILAN BARU)
# ==========================================
st.set_page_config(page_title="INTRINSIK.AI", page_icon="📈", layout="wide")

# Injeksi CSS untuk tampilan modern
st.markdown("""
    <style>
    /* Mengubah font utama */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Container untuk Logo dan Judul */
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 5px;
    }
    
    /* Emoji Ikon */
    .logo-icon {
        font-size: 50px;
        line-height: 1;
    }
    
    /* Judul Utama dengan Gradasi */
    .main-title { 
        font-size: 50px; 
        font-weight: 800; 
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #60A5FA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: transparent;
        margin: 0;
    }
    
    /* Sub-judul */
    .sub-title { 
        font-size: 18px; 
        color: #9CA3AF; 
        margin-bottom: 30px;
        margin-top: 5px;
    }
    
    /* Kotak Card untuk Hasil Analisis */
    .verdict-card {
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .verdict-green { background-color: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; }
    .verdict-red { background-color: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; }
    .verdict-title { font-size: 16px; font-weight: 600; color: #D1D5DB; text-transform: uppercase; letter-spacing: 1px;}
    .verdict-value { font-size: 40px; font-weight: 800; margin: 10px 0; }
    .verdict-green .verdict-value { color: #10B981; }
    .verdict-red .verdict-value { color: #EF4444; }
    .verdict-desc { font-size: 16px; color: #E5E7EB; }
    </style>
""", unsafe_allow_html=True)

# Tampilan Header (Emoji dan Teks dipisah agar emoji tidak berubah warna)
st.markdown("""
    <div class="header-container">
        <div class="logo-icon">📈</div>
        <div class="main-title">INTRINSIK.AI</div>
    </div>
    <div class="sub-title">Robo-Advisor Valuasi Fundamental & Analisis Investasi</div>
""", unsafe_allow_html=True)


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
    ticker = st.text_input("Kode Saham (Manual)", value="ICBP", help="Masukkan kode saham 4 huruf")
    harga_pasar = st.number_input("Harga Saham Pasar (Rp)", min_value=100, value=10000, step=100)
    
    st.divider()
    st.markdown("### 📄 Unggah Dokumen")
    uploaded_file = st.file_uploader("Upload Laporan Keuangan (PDF)", type=["pdf"])
    
    st.divider()
    demo_mode = st.toggle("🛠️ Demo Mode (Simulasi)", help="Aktifkan jika internet mati/error")
    st.caption("Jika aktif, sistem tidak memanggil API Google.")
    
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
# 5. TAMPILAN VERIFIKASI (HITL) & PRATINJAU PDF
# ==========================================
if st.session_state['analisis_selesai']:
    data_keuangan = st.session_state['data_keuangan']
    
    st.markdown("### 🔍 Verifikasi Data Ekstraksi AI")
    
    # Tampilkan info periode dalam bentuk kotak sukses
    st.success(f"**Periode Laporan Terdeteksi AI:** {data_keuangan.get('periode_laporan', 'Tidak diketahui')}")
    
    col_gambar, col_form = st.columns([1, 1], gap="large")
    
    # --- KOLOM KIRI: GAMBAR PDF ---
    with col_gambar:
        with st.container(border=True):
            st.markdown("#### 📄 Pratinjau Halaman PDF")
            
            metrik_pilihan = st.selectbox(
                "Pilih data untuk melihat sumber halamannya:",
                ["Laba Bersih", "Total Ekuitas", "Arus Kas (CFO/CFI/CFF)", "Jumlah Saham"]
            )
            
            if metrik_pilihan == "Laba Bersih":
                hal_target = data_keuangan.get('hal_laba', 1)
            elif metrik_pilihan == "Total Ekuitas":
                hal_target = data_keuangan.get('hal_ekuitas', 1)
            elif metrik_pilihan == "Arus Kas (CFO/CFI/CFF)":
                hal_target = data_keuangan.get('hal_arus_kas', 1)
            else:
                hal_target = data_keuangan.get('hal_saham', 1)

            try:
                pdf_document = fitz.open(stream=st.session_state['pdf_bytes'], filetype="pdf")
                page = pdf_document.load_page(hal_target - 1) 
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_bytes = pix.tobytes("png")
                st.image(img_bytes, caption=f"Halaman {hal_target}", use_container_width=True)
            except Exception as e:
                st.error(f"Gagal memuat pratinjau: {e}")

    # --- KOLOM KANAN: FORM HITL ---
    with col_form:
        with st.container(border=True):
            st.markdown("#### 📝 Form Verifikasi (HITL)")
            st.info("Periksa dan perbaiki jika ada angka yang salah dibaca AI.")
            
            with st.form("form_hitl"):
                laba_bersih = st.number_input("Laba Bersih (Juta Rp)", value=int(data_keuangan['laba_bersih_juta']))
                ekuitas = st.number_input("Total Ekuitas (Juta Rp)", value=int(data_keuangan['total_ekuitas_juta']))
                net_cfo = st.number_input("Net CFO (Juta Rp)", value=int(data_keuangan['net_cfo_juta']))
                net_cfi = st.number_input("Net CFI (Juta Rp)", value=int(data_keuangan['net_cfi_juta']))
                net_cff = st.number_input("Net CFF (Juta Rp)", value=int(data_keuangan['net_cff_juta']))
                saham = st.number_input("Jumlah Saham Beredar", value=int(data_keuangan['jumlah_saham']))
                
                submit_hitl = st.form_submit_button("✅ Data Sudah Benar, Hitung Valuasi!", use_container_width=True, type="primary")
                
    if submit_hitl:
        data_final = {
            "laba_bersih_juta": laba_bersih, "total_ekuitas_juta": ekuitas,
            "net_cfo_juta": net_cfo, "net_cfi_juta": net_cfi, "net_cff_juta": net_cff, "jumlah_saham": saham
        }
        st.session_state['hasil'] = hitung_valuasi(data_final, harga_pasar)
        st.session_state['hitung_selesai'] = True

# ==========================================
# 6. DASHBOARD HASIL AKHIR (TAMPILAN CARD MODERN)
# ==========================================
if st.session_state['hitung_selesai']:
    hasil = st.session_state['hasil']
    data_keuangan = st.session_state['data_keuangan']
    
    st.divider()
    st.markdown(f"### 📊 Hasil Analisis: {ticker} ({data_keuangan.get('periode_laporan', '')})")
    
    # Cek Status Valuasi
    is_undervalued = harga_pasar < hasil['nilai_intrinsik']
    
    # HTML Card untuk Verdict
    if is_undervalued:
        card_class = "verdict-green"
        status_text = "UNDERVALUED (MURAH)"
        desc_text = f"Potensi Keuntungan (Upside): +{hasil['mos']:.2f}%"
    else:
        card_class = "verdict-red"
        status_text = "OVERVALUED (MAHAL)"
        desc_text = f"Risiko Penurunan (Downside): {hasil['mos']:.2f}%"
        
    st.markdown(f"""
        <div class="verdict-card {card_class}">
            <div class="verdict-title">Harga Wajar (Nilai Intrinsik DCF)</div>
            <div class="verdict-value">Rp {hasil['nilai_intrinsik']:,.2f}</div>
            <div class="verdict-desc">
                Harga Pasar Saat Ini: <b>Rp {harga_pasar:,.0f}</b> <br>
                Status: <b>{status_text}</b> | {desc_text}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs Detail
    tab1, tab2, tab3 = st.tabs(["📑 Rasio Relatif", "📈 Proyeksi DCF", "🩺 Kesehatan"])
    
    with tab1:
        df_rasio = pd.DataFrame({
            "Metrik": ["Earnings Per Share (EPS)", "Book Value Per Share (BVPS)", "Price to Earnings (PER)", "Price to Book Value (PBV)"],
            "Nilai": [f"Rp {hasil['eps']:,.2f}", f"Rp {hasil['bvps']:,.2f}", f"{hasil['per']:,.2f} x", f"{hasil['pbv']:,.2f} x"]
        })
        st.dataframe(df_rasio, use_container_width=True, hide_index=True)
        
    with tab2:
        df_dcf = pd.DataFrame({
            "Tahun Ke-": range(1, 11),
            "Proyeksi Laba (Juta Rp)": [f"{x:,.2f}" for x in hasil['projected_income']],
            "Discounted (Juta Rp)": [f"{x:,.2f}" for x in hasil['discounted_income']]
        })
        st.dataframe(df_dcf, use_container_width=True, hide_index=True)
        
        col_tv1, col_tv2 = st.columns(2)
        col_tv1.info(f"**Terminal Value:**\nRp {hasil['terminal_value']:,.2f} Juta")
        col_tv2.success(f"**Total Valuasi (Equity Value):**\nRp {hasil['total_valuasi_juta']:,.2f} Juta")
        
    with tab3:
        if hasil['is_sehat']:
            st.success("✅ Status: **PERUSAHAAN SEHAT** (Arus kas operasi positif, sedang ekspansi aset, dan mampu membayar kewajiban).")
        else:
            st.warning("⚠️ Status: **PERLU WASPADA** (Cek kembali arus kas perusahaan. Bisa jadi ada indikasi masalah keuangan).")