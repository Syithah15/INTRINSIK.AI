import streamlit as st
import pandas as pd
import pymupdf as fitz
from ai_engine import ekstrak_data_pdf
from calculator import hitung_valuasi

# ==========================================
# 1. KONFIGURASI HALAMAN & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="INTRINSIK.AI", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .header-container { display: flex; align-items: center; gap: 20px; margin-bottom: 5px; }
    .logo-icon { font-size: 50px; line-height: 1; }
    
    .main-title { 
        font-size: 50px; font-weight: 800; 
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #60A5FA 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; color: transparent; margin: 0;
    }
    .sub-title { font-size: 18px; color: #9CA3AF; margin-bottom: 30px; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

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
    ticker = st.text_input("Kode Saham (Manual)", value="ICBP")
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
    st.success(f"**Periode Laporan Terdeteksi AI:** {data_keuangan.get('periode_laporan', 'Tidak diketahui')}")
    
    col_gambar, col_form = st.columns([1, 1], gap="large")
    
    # --- KOLOM KIRI: GAMBAR PDF ---
    with col_gambar:
        with st.container(border=True):
            st.markdown("#### 📄 Pratinjau Halaman PDF")
            
            # DROPDOWN DIPERBARUI: Menambahkan Pendapatan dan Liabilitas
            metrik_pilihan = st.selectbox(
                "Pilih data untuk melihat sumber halamannya:",
                ["Laba Bersih", "Total Ekuitas", "Total Pendapatan", "Total Liabilitas", "Arus Kas (CFO/CFI/CFF)", "Jumlah Saham"]
            )
            
            # LOGIKA PEMILIHAN HALAMAN DIPERBARUI
            if metrik_pilihan == "Laba Bersih":
                hal_target = data_keuangan.get('hal_laba', 1)
            elif metrik_pilihan == "Total Ekuitas":
                hal_target = data_keuangan.get('hal_ekuitas', 1)
            elif metrik_pilihan == "Total Pendapatan":
                hal_target = data_keuangan.get('hal_pendapatan', 1)
            elif metrik_pilihan == "Total Liabilitas":
                hal_target = data_keuangan.get('hal_liabilitas', 1)
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
# 6. DASHBOARD HASIL AKHIR (4 OUTPUT UTAMA)
# ==========================================
if st.session_state['hitung_selesai']:
    hasil = st.session_state['hasil']
    data_keuangan = st.session_state['data_keuangan']
    
    st.divider()
    st.markdown("## 📋 Laporan Hasil Analisis Fundamental")
    
    # --- BAGIAN 1: INFORMASI PERUSAHAAN ---
    st.markdown("### 1. Informasi Perusahaan")
    info_data = {
        "Keterangan": ["Nama Perusahaan", "Kode Saham", "Periode Laporan", "Harga Saham Terakhir", "Jumlah Saham Beredar", "Market Cap (Rp)"],
        "Nilai": [
            data_keuangan.get('nama_perusahaan', '-'), ticker, data_keuangan.get('periode_laporan', '-'),
            f"Rp {harga_pasar:,.0f}", f"{int(data_keuangan['jumlah_saham']):,}", f"Rp {hasil['market_cap']:,.0f}"
        ]
    }
    st.table(pd.DataFrame(info_data))
    
    # --- BAGIAN 2: VALUASI RELATIF ---
    st.markdown("### 2. Valuasi Relatif")
    relatif_data = {
        "Metrik / Rasio": ["EPS (Earnings per Share)", "PER (Price to Earnings)", "BVPS (Book Value per Share)", "PBV (Price to Book)", "PSR (Price to Sales)", "CPS (Cash per Share)", "PCS (Price to Cash)", "REPS (Retained Earning per Share)", "PRER (Price to REPS)"],
        "Nilai": [
            f"Rp {hasil['eps']:,.2f}", f"{hasil['per']:,.2f} x", 
            f"Rp {hasil['bvps']:,.2f}", f"{hasil['pbv']:,.2f} x", 
            f"{hasil['psr']:,.2f} x", f"Rp {hasil['cps']:,.2f}", f"{hasil['pcs']:,.2f} x", 
            f"Rp {hasil['reps']:,.2f}", f"{hasil['prer']:,.2f} x"
        ],
        "Keterangan (Status)": [
            "🟢 Laba Positif" if hasil['eps'] > 0 else "🔴 Laba Negatif",
            "🟢 Murah (< 10x)" if hasil['per'] < 10 else ("🟡 Wajar (10x-20x)" if hasil['per'] <= 20 else "🔴 Mahal (> 20x)"),
            "🟢 Di atas Harga Pasar" if hasil['bvps'] > harga_pasar else "🟡 Di bawah Harga Pasar",
            "🟢 Murah (< 1.0x)" if hasil['pbv'] < 1.0 else ("🟡 Wajar (1.0x-2.5x)" if hasil['pbv'] <= 2.5 else "🔴 Mahal (> 2.5x)"),
            "🟢 Murah (< 1.5x)" if hasil['psr'] < 1.5 else ("🟡 Wajar (1.5x-3.0x)" if hasil['psr'] <= 3.0 else "🔴 Mahal (> 3.0x)"),
            "🟢 Kas Kuat (> 10% Harga)" if hasil['cps'] > (harga_pasar * 0.1) else "🟡 Kas Terbatas",
            "🟢 Murah (< 5x)" if hasil['pcs'] < 5 else ("🟡 Wajar (5x-15x)" if hasil['pcs'] <= 15 else "🔴 Mahal (> 15x)"),
            "🟢 Laba Ditahan Positif" if hasil['reps'] > 0 else "🔴 Laba Ditahan Negatif",
            "🟢 Murah (< 3.0x)" if hasil['prer'] < 3.0 else ("🟡 Wajar (3.0x-8.0x)" if hasil['prer'] <= 8.0 else "🔴 Mahal (> 8.0x)")
        ]
    }
    st.table(pd.DataFrame(relatif_data))

    # --- BAGIAN 3: VALUASI ABSOLUT (DCF) ---
    st.markdown("### 3. Valuasi Absolut (Discounted Cash Flow)")
    st.write("**Asumsi:** Discount Rate = 11% | Perpetual Growth Rate = 3% | Proyeksi = 10 Tahun")
    
    df_dcf = pd.DataFrame({
        "Tahun Ke-": range(1, 11),
        "Laba Bersih (Juta Rp)": [f"{x:,.2f}" for x in hasil['projected_income']],
        "Discounted (Juta Rp)": [f"{x:,.2f}" for x in hasil['discounted_income']]
    })
    st.dataframe(df_dcf, use_container_width=True, hide_index=True)
    
    st.markdown(f"""
    <table style="width:100%; border-collapse: collapse; margin-bottom: 20px;">
        <tr style="border-bottom: 1px solid #555;"><td style="padding: 8px; font-weight: bold;">Terminal Value (Juta Rp)</td><td style="padding: 8px; text-align: right;">Rp {hasil['terminal_value']:,.2f}</td></tr>
        <tr style="border-bottom: 1px solid #555;"><td style="padding: 8px; font-weight: bold;">Terminal Value Discounted</td><td style="padding: 8px; text-align: right;">Rp {hasil['discounted_tv']:,.2f}</td></tr>
        <tr style="border-bottom: 1px solid #555;"><td style="padding: 8px; font-weight: bold;">Total Discounted Laba Bersih</td><td style="padding: 8px; text-align: right;">Rp {hasil['total_pv']:,.2f}</td></tr>
        <tr style="border-top: 2px solid #fff; border-bottom: 2px solid #fff;">
            <td style="padding: 8px; font-weight: bold; font-size: 18px;">Total Valuasi (Equity Value)</td>
            <td style="padding: 8px; text-align: right; font-weight: bold; font-size: 18px;">Rp {hasil['total_valuasi_juta']:,.2f} Juta</td>
        </tr>
        <tr><td style="padding: 8px; font-weight: bold;">Jumlah Saham Beredar</td><td style="padding: 8px; text-align: right;">{int(data_keuangan['jumlah_saham']):,}</td></tr>
        <tr style="background-color: #1f2937;">
            <td style="padding: 12px; font-weight: bold; font-size: 22px; color: #10B981;">NILAI INTRINSIK PER LEMBAR</td>
            <td style="padding: 12px; text-align: right; font-weight: bold; font-size: 22px; color: #10B981;">Rp {hasil['nilai_intrinsik']:,.2f}</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    is_undervalued = harga_pasar < hasil['nilai_intrinsik']
    if is_undervalued:
        st.success(f"**Verdict: UNDERVALUED (MURAH)**. Harga pasar saat ini (Rp {harga_pasar:,.0f}) berada di bawah nilai intrinsik. Potensi Upside: **+{hasil['mos']:.2f}%**")
    else:
        st.error(f"**Verdict: OVERVALUED (MAHAL)**. Harga pasar saat ini (Rp {harga_pasar:,.0f}) berada di atas nilai intrinsik. Risiko Downside: **{hasil['mos']:.2f}%**")

    # --- BAGIAN 4: KESEHATAN PERUSAHAAN ---
    st.markdown("### 4. Kesehatan Perusahaan (Screening)")
    cfo_ok = data_keuangan['net_cfo_juta'] > 0
    cfi_ok = data_keuangan['net_cfi_juta'] < 0
    cff_ok = data_keuangan['net_cff_juta'] < 0
    
    sehat_data = {
        "Indikator": ["Net CFO (Arus Kas Operasi)", "Net CFI (Arus Kas Investasi)", "Net CFF (Arus Kas Pendanaan)", "ROE (Return on Equity)", "DER (Debt to Equity)", "NPM (Net Profit Margin)"],
        "Nilai": [
            f"Rp {data_keuangan['net_cfo_juta']:,.0f} Juta", f"Rp {data_keuangan['net_cfi_juta']:,.0f} Juta", f"Rp {data_keuangan['net_cff_juta']:,.0f} Juta",
            f"{hasil['roe']:.2f} %", f"{hasil['der']:.2f} x", f"{hasil['npm']:.2f} %"
        ],
        "Keterangan": [
            "🟢 Sehat (Arus kas operasi positif)" if cfo_ok else "🔴 Waspada (Arus kas operasi negatif)",
            "🟢 Sehat (Ekspansi aset)" if cfi_ok else "🟡 Waspada (Divestasi/Masalah aset)",
            "🟢 Sehat (Bayar utang/dividen)" if cff_ok else "🟡 Waspada (Cari utang baru)",
            "🟢 Sangat Bagus (>15%)" if hasil['roe'] > 15 else ("🟡 Wajar (5%-15%)" if hasil['roe'] >= 5 else "🔴 Kurang (<5%)"),
            "🟢 Aman (<1.0x)" if hasil['der'] < 1.0 else ("🟡 Wajar (1.0x-2.0x)" if hasil['der'] <= 2.0 else "🔴 Berisiko (>2.0x)"),
            "🟢 Sangat Bagus (>15%)" if hasil['npm'] > 15 else ("🟡 Wajar (5%-15%)" if hasil['npm'] >= 5 else "🔴 Kurang (<5%)")
        ]
    }
    st.table(pd.DataFrame(sehat_data))