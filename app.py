import streamlit as st
import pandas as pd
import pymupdf as fitz
from ai_engine import ekstrak_data_pdf
from calculator import hitung_valuasi

# ==========================================
# 1. KONFIGURASI HALAMAN & TAMPILAN
# ==========================================
st.set_page_config(page_title="INTRINSIK.AI", page_icon="📈", layout="wide")
st.markdown("""
    <style>
    .main-title { font-size: 45px; font-weight: 800; color: #1E3A8A; margin-bottom: 0px;}
    .sub-title { font-size: 18px; color: #6B7280; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)
st.markdown('<div class="main-title">📈 INTRINSIK.AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Robo-Advisor Valuasi Fundamental & Analisis Investasi</div>', unsafe_allow_html=True)

# ==========================================
# 2. INISIALISASI SESSION STATE
# ==========================================
if 'analisis_selesai' not in st.session_state:
    st.session_state['analisis_selesai'] = False
if 'hitung_selesai' not in st.session_state:
    st.session_state['hitung_selesai'] = False

# ==========================================
# 3. SIDEBAR: INPUT DATA (Tahun & Kuartal Dihapus)
# ==========================================
with st.sidebar:
    st.header("📥 Input Data")
    ticker = st.text_input("Kode Saham (Manual)", value="ICBP")
    harga_pasar = st.number_input("Harga Saham Pasar (Rp)", min_value=100, value=10000, step=100)
    
    st.divider()
    st.header("📄 Unggah Dokumen")
    uploaded_file = st.file_uploader("Upload Laporan Keuangan (PDF)", type=["pdf"])
    
    demo_mode = st.checkbox("🛠️ Gunakan Data Simulasi (Demo Mode)")
    tombol_analisis = st.button("🚀 Mulai Analisis", use_container_width=True, type="primary")

# ==========================================
# 4. LOGIKA PROSES ANALISIS
# ==========================================
if tombol_analisis:
    if uploaded_file is None:
        st.warning("⚠️ Silakan unggah file PDF terlebih dahulu!")
    else:
        st.session_state['analisis_selesai'] = False
        st.session_state['hitung_selesai'] = False
        
        with st.spinner("AI sedang membaca isi dokumen..."):
            st.session_state['pdf_bytes'] = uploaded_file.getvalue()
            hasil_ai = ekstrak_data_pdf(uploaded_file, is_demo=demo_mode)
            
            if hasil_ai["status"] in ["invalid", "error"]:
                st.error(hasil_ai["pesan"])
            else:
                st.session_state['data_keuangan'] = hasil_ai["data"]
                st.session_state['analisis_selesai'] = True

# ==========================================
# 5. TAMPILAN VERIFIKASI (HITL) & PRATINJAU PDF INTERAKTIF
# ==========================================
if st.session_state['analisis_selesai']:
    data_keuangan = st.session_state['data_keuangan']
    
    st.subheader("🔍 Verifikasi Data Ekstraksi AI")
    
    # Menampilkan Periode Laporan yang dibaca AI
    st.info(f"📅 **Periode Laporan Terdeteksi AI:** {data_keuangan.get('periode_laporan', 'Tidak diketahui')}")
    
    col_gambar, col_form = st.columns([1, 1])
    
    # --- KOLOM KIRI: GAMBAR PDF DINAMIS ---
    with col_gambar:
        st.write("📄 **Pratinjau Halaman PDF**")
        
        # Fitur Dropdown: Pilih metrik untuk melihat halamannya
        metrik_pilihan = st.selectbox(
            "Pilih data untuk melihat sumber halamannya di PDF:",
            ["Laba Bersih", "Total Ekuitas", "Arus Kas (CFO/CFI/CFF)", "Jumlah Saham"]
        )
        
        # Tentukan halaman berdasarkan pilihan
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
            st.error(f"Gagal memuat pratinjau PDF: {e}")

    # --- KOLOM KANAN: FORM HITL ---
    with col_form:
        st.info("📝 Form Verifikasi (HITL)")
        with st.form("form_hitl"):
            # Ticker diambil dari sidebar
            laba_bersih = st.number_input("Laba Bersih (Juta Rp)", value=int(data_keuangan['laba_bersih_juta']))
            ekuitas = st.number_input("Total Ekuitas (Juta Rp)", value=int(data_keuangan['total_ekuitas_juta']))
            net_cfo = st.number_input("Net CFO (Juta Rp)", value=int(data_keuangan['net_cfo_juta']))
            net_cfi = st.number_input("Net CFI (Juta Rp)", value=int(data_keuangan['net_cfi_juta']))
            net_cff = st.number_input("Net CFF (Juta Rp)", value=int(data_keuangan['net_cff_juta']))
            saham = st.number_input("Jumlah Saham Beredar", value=int(data_keuangan['jumlah_saham']))
            
            submit_hitl = st.form_submit_button("✅ Data Sudah Benar, Hitung Valuasi!", use_container_width=True)
            
    if submit_hitl:
        data_final = {
            "laba_bersih_juta": laba_bersih, "total_ekuitas_juta": ekuitas,
            "net_cfo_juta": net_cfo, "net_cfi_juta": net_cfi, "net_cff_juta": net_cff, "jumlah_saham": saham
        }
        st.session_state['hasil'] = hitung_valuasi(data_final, harga_pasar)
        st.session_state['hitung_selesai'] = True

# ==========================================
# 6. DASHBOARD HASIL AKHIR
# ==========================================
if st.session_state['hitung_selesai']:
    hasil = st.session_state['hasil']
    data_keuangan = st.session_state['data_keuangan']
    
    st.divider()
    st.subheader(f"📊 Hasil Analisis: {ticker} ({data_keuangan.get('periode_laporan', '')})")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Harga Pasar", f"Rp {harga_pasar:,.0f}")
    m2.metric("Nilai Intrinsik (DCF)", f"Rp {hasil['nilai_intrinsik']:,.2f}")
    
    if harga_pasar < hasil['nilai_intrinsik']:
        m3.success(f"🟢 UNDERVALUED\nMargin: +{hasil['mos']:.2f}%")
    else:
        m3.error(f"🔴 OVERVALUED\nMargin: {hasil['mos']:.2f}%")
    
    tab1, tab2, tab3 = st.tabs(["📑 Rasio Relatif", "📈 Proyeksi DCF", "🩺 Kesehatan"])
    
    with tab1:
        df_rasio = pd.DataFrame({
            "Metrik": ["EPS", "BVPS", "PER", "PBV"],
            "Nilai": [f"Rp {hasil['eps']:,.2f}", f"Rp {hasil['bvps']:,.2f}", f"{hasil['per']:,.2f} x", f"{hasil['pbv']:,.2f} x"]
        })
        st.table(df_rasio)
        
    with tab2:
        df_dcf = pd.DataFrame({
            "Tahun Ke-": range(1, 11),
            "Proyeksi Laba (Juta Rp)": [f"{x:,.2f}" for x in hasil['projected_income']],
            "Discounted (Juta Rp)": [f"{x:,.2f}" for x in hasil['discounted_income']]
        })
        st.dataframe(df_dcf, use_container_width=True)
        st.info(f"Terminal Value: Rp {hasil['terminal_value']:,.2f} Juta | Discounted TV: Rp {hasil['discounted_tv']:,.2f} Juta")
        st.success(f"Total Valuasi (Equity Value): Rp {hasil['total_valuasi_juta']:,.2f} Juta")
        
    with tab3:
        if hasil['is_sehat']:
            st.success("✅ Status: PERUSAHAAN SEHAT (Arus kas operasi positif, ekspansi aset)")
        else:
            st.warning("⚠️ Status: PERLU WASPADA (Cek kembali arus kas perusahaan)")