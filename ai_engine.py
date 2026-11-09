import streamlit as st
from google import genai
from google.genai import types
import json

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_CANDIDATES = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash"]

def ekstrak_data_pdf(file_pdf, is_demo=False):
    
    if is_demo:
        return {
            "status": "success",
            "data": {
                "nama_perusahaan": "PT Indofood CBP Sukses Makmur Tbk",
                "periode_laporan": "Q2 2026 (30 Juni 2026)",
                "laba_bersih_juta": 3702564,
                "total_ekuitas_juta": 75272636,
                "total_pendapatan_juta": 41863388,
                "total_liabilitas_juta": 68713288,
                "net_cfo_juta": 5672816,
                "net_cfi_juta": -1312002,
                "net_cff_juta": -974863,
                "jumlah_saham": 11661908000,
                "total_kas_juta": 33537992,          
                "laba_ditahan_juta": 45794427,       
                "hal_laba": 8, 
                "hal_ekuitas": 6,
                "hal_pendapatan": 7,    
                "hal_liabilitas": 5,    
                "hal_arus_kas": 10,
                "hal_saham": 6
            }
        }

    pdf_bytes = file_pdf.read()
    prompt = """
    Anda adalah analis keuangan senior. Periksa dokumen yang dilampirkan.
    1. JIKA BUKAN laporan keuangan, kembalikan: {"status": "invalid", "pesan": "Dokumen tidak valid."}
    
    2. JIKA VALID, ekstrak data berikut. PERHATIKAN SATUANNYA (Juta atau Miliar Rupiah):
       - nama_perusahaan
       - periode_laporan (Format wajib: "Q[1/2/3/4] [Tahun] (Tanggal Lengkap)")
       - laba_bersih_juta: (Cari "Laba periode berjalan yang dapat diatribusikan kepada Pemilik Entitas Induk". JANGAN ambil angka "Laba per Saham (EPS)". Jika laporan dalam MILIAR, kalikan dengan 1000 agar menjadi JUTA).
       - total_ekuitas_juta (Jika laporan dalam MILIAR, kalikan dengan 1000).
       - total_pendapatan_juta (Jika laporan dalam MILIAR, kalikan dengan 1000).
       - total_liabilitas_juta (Jika laporan dalam MILIAR, kalikan dengan 1000).
       - total_kas_juta (Jika laporan dalam MILIAR, kalikan dengan 1000).
       - laba_ditahan_juta (Cari "Saldo laba" di bagian Ekuitas. Jika MILIAR, kalikan dengan 1000).
       - net_cfo_juta (Jika laporan dalam MILIAR, kalikan dengan 1000).
       - net_cfi_juta (Jika laporan dalam MILIAR, kalikan dengan 1000).
       - net_cff_juta (Jika laporan dalam MILIAR, kalikan dengan 1000).
       - jumlah_saham (Cari di Catatan Laporan Keuangan pada bagian "Modal Saham". Jika tidak ada, hitung dengan rumus: (Modal Saham / Nilai Nominal per Saham) - (Saham Diperoleh Kembali / Nilai Nominal). Angka ini dalam satuan Lembar Penuh).
       - hal_laba, hal_ekuitas, hal_pendapatan, hal_liabilitas, hal_arus_kas, hal_saham (nomor halaman)
       
    Kembalikan HANYA format JSON ini:
    {"status": "success", "data": {"nama_perusahaan": "...", "periode_laporan": "Q2 2026 (30 Juni 2026)", "laba_bersih_juta": 1234, "total_ekuitas_juta": 5678, "total_pendapatan_juta": 999, "total_liabilitas_juta": 888, "total_kas_juta": 111, "laba_ditahan_juta": 222, "net_cfo_juta": 901, "net_cfi_juta": -234, "net_cff_juta": -567, "jumlah_saham": 1000000, "hal_laba": 8, "hal_ekuitas": 6, "hal_pendapatan": 7, "hal_liabilitas": 5, "hal_arus_kas": 10, "hal_saham": 6}}
    """
    
    last_error = ""
    for model_id in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=[types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf'), prompt]
            )
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:-3].strip()
            return json.loads(response_text)
        except Exception as e:
            last_error = str(e)
            continue
            
    return {"status": "error", "pesan": f"Gagal: {last_error}"}