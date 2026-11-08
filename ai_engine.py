import streamlit as st
from google import genai
from google.genai import types
import json

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_CANDIDATES = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash"]

def ekstrak_data_pdf(file_pdf, is_demo=False):
    
    # --- JIKA USER MENCENTANG DEMO MODE ---
    if is_demo:
        return {
            "status": "success",
            "data": {
                "nama_perusahaan": "PT Indofood CBP Sukses Makmur Tbk",
                "periode_laporan": "30 Juni 2026 (Q2 2026)",
                "laba_bersih_juta": 4537446,
                "total_ekuitas_juta": 75272636,
                "net_cfo_juta": 5672816,
                "net_cfi_juta": -1312002,
                "net_cff_juta": -974863,
                "jumlah_saham": 11661908000,
                # AI mencatat halaman spesifik tiap metrik
                "hal_laba": 7,
                "hal_ekuitas": 6,
                "hal_arus_kas": 10,
                "hal_saham": 6
            }
        }

    # --- JIKA USER TIDAK MENCENTANG (MODE ASLI) ---
    pdf_bytes = file_pdf.read()
    prompt = """
    Anda adalah analis keuangan senior. Periksa dokumen yang dilampirkan.
    1. JIKA BUKAN laporan keuangan, kembalikan: {"status": "invalid", "pesan": "Dokumen tidak valid."}
    2. JIKA VALID, ekstrak data berikut (dalam Jutaan Rupiah):
       - nama_perusahaan
       - periode_laporan (contoh format: "31 Desember 2025" atau "30 Juni 2026")
       - laba_bersih_juta
       - total_ekuitas_juta
       - net_cfo_juta
       - net_cfi_juta
       - net_cff_juta
       - jumlah_saham
       - hal_laba (nomor halaman tempat Laba Bersih berada)
       - hal_ekuitas (nomor halaman tempat Ekuitas berada)
       - hal_arus_kas (nomor halaman tempat Arus Kas berada)
       - hal_saham (nomor halaman tempat Jumlah Saham berada)
       
    Kembalikan HANYA format JSON ini:
    {"status": "success", "data": {"nama_perusahaan": "...", "periode_laporan": "...", "laba_bersih_juta": 1234, "total_ekuitas_juta": 5678, "net_cfo_juta": 901, "net_cfi_juta": -234, "net_cff_juta": -567, "jumlah_saham": 1000000, "hal_laba": 7, "hal_ekuitas": 6, "hal_arus_kas": 10, "hal_saham": 6}}
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