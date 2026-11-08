# 📈 INTRINSIK.AI
**Robo-Advisor Valuasi Fundamental & Analisis Investasi**

INTRINSIK.AI adalah sebuah aplikasi berbasis web (Web App) yang dirancang untuk mengotomatisasi analisis fundamental saham. Aplikasi ini mengekstrak data dari laporan keuangan perusahaan (PDF) menggunakan *Vision-Language Model* (VLM) dan menghitung nilai intrinsik (harga wajar) saham menggunakan metode *Discounted Cash Flow* (DCF) serta Valuasi Relatif.

Dikembangkan untuk **Lomba Karya Tulis Ilmiah (LKTI) IT FEST Universitas Halu Oleo 2026**.


## 👥 Tim Pengembang
**Nama Tim:** AITEK

MASYITHAH (Ketua Tim) - ILMU KOMPUTER - F1G125061

MUHAMMAD ALGI ALAMSYAH PUTRA (Anggota) - EKONOMI PEMBANGUNAN - B1A125116

FATIMAH ALYA SHABIRAH (Anggota) - ILMU KOMPUTER - F1G125005

Perguruan Tinggi: Universitas Halu Oleo
---

## ✨ Fitur Utama
1. **Ekstraksi PDF Otomatis:** Membaca laporan keuangan (PDF) menggunakan AI Gemini (VLM).
2. **Human-in-the-Loop (HITL):** Antarmuka verifikasi ganda yang menampilkan pratinjau halaman PDF asli di samping form input.
3. **Valuasi Absolut (DCF):** Menghitung nilai intrinsik per lembar saham.
4. **Valuasi Relatif:** Menghitung rasio PER, PBV, EPS, dan BVPS.
5. **Mode Simulasi (Demo):** Fitur cadangan (*fallback*) jika koneksi internet terputus saat presentasi.

---

## 🚀 Cara Menjalankan Secara Lokal

1. **Clone repositori ini:**
   ```bash
   git clone https://github.com/Syithah15/INTRINSIK.AI.git
   cd IntrinsikAI