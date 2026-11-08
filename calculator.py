def hitung_valuasi(data_mentah, harga_pasar):
    # Konversi Satuan
    laba_bersih = data_mentah['laba_bersih_juta'] * 1_000_000
    total_ekuitas = data_mentah['total_ekuitas_juta'] * 1_000_000
    total_pendapatan = data_mentah.get('total_pendapatan_juta', 1) * 1_000_000 # Hindari pembagian nol
    total_liabilitas = data_mentah.get('total_liabilitas_juta', 0) * 1_000_000
    total_kas = data_mentah.get('total_kas_juta', 0) * 1_000_000
    laba_ditahan = data_mentah.get('laba_ditahan_juta', 0) * 1_000_000
    jumlah_saham = data_mentah['jumlah_saham'] 
    
    # Metrik Dasar per Saham
    eps = laba_bersih / jumlah_saham if jumlah_saham > 0 else 0
    bvps = total_ekuitas / jumlah_saham if jumlah_saham > 0 else 0
    cps = total_kas / jumlah_saham if jumlah_saham > 0 else 0
    reps = laba_ditahan / jumlah_saham if jumlah_saham > 0 else 0
    sps = total_pendapatan / jumlah_saham if jumlah_saham > 0 else 0 # Sales per Share
    
    # Valuasi Relatif
    per = harga_pasar / eps if eps != 0 else 0
    pbv = harga_pasar / bvps if bvps != 0 else 0
    pcs = harga_pasar / cps if cps != 0 else 0
    prer = harga_pasar / reps if reps != 0 else 0
    psr = harga_pasar / sps if sps != 0 else 0
    
    # Rasio Profitabilitas & Solvabilitas
    roe = (laba_bersih / total_ekuitas) * 100 if total_ekuitas != 0 else 0
    der = total_liabilitas / total_ekuitas if total_ekuitas != 0 else 0
    npm = (laba_bersih / total_pendapatan) * 100 if total_pendapatan != 0 else 0

    # DCF
    discount_rate = 0.11
    perpetual_growth = 0.03
    proyeksi_growth = 0.04
    
    projected_income = []
    discounted_income = []
    current_income = data_mentah['laba_bersih_juta']
    
    for i in range(1, 11):
        current_income = current_income * (1 + proyeksi_growth)
        projected_income.append(current_income)
        pv = current_income / ((1 + discount_rate) ** i)
        discounted_income.append(pv)
        
    total_pv = sum(discounted_income)
    terminal_value = (projected_income[-1] * (1 + perpetual_growth)) / (discount_rate - perpetual_growth)
    discounted_tv = terminal_value / ((1 + discount_rate) ** 10)
    
    total_valuasi_juta = total_pv + discounted_tv
    total_valuasi_penuh = total_valuasi_juta * 1_000_000
    nilai_intrinsik = total_valuasi_penuh / jumlah_saham if jumlah_saham > 0 else 0
    mos = ((nilai_intrinsik - harga_pasar) / nilai_intrinsik) * 100 if nilai_intrinsik > 0 else 0

    return {
        "eps": eps, "bvps": bvps, "per": per, "pbv": pbv,
        "cps": cps, "pcs": pcs, "reps": reps, "prer": prer, "psr": psr,
        "roe": roe, "der": der, "npm": npm,
        "nilai_intrinsik": nilai_intrinsik, "mos": mos,
        "projected_income": projected_income,
        "discounted_income": discounted_income,
        "terminal_value": terminal_value,
        "discounted_tv": discounted_tv,
        "total_pv": total_pv,
        "total_valuasi_juta": total_valuasi_juta,
        "market_cap": harga_pasar * jumlah_saham
    }