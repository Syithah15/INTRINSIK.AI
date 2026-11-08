def hitung_valuasi(data_mentah, harga_pasar):
    # --- KONVERSI SATUAN (Jutaan ke Rupiah Penuh) ---
    laba_bersih = data_mentah['laba_bersih_juta'] * 1_000_000
    total_ekuitas = data_mentah['total_ekuitas_juta'] * 1_000_000
    jumlah_saham = data_mentah['jumlah_saham'] 
    
    # --- METRIK DASAR ---
    eps = laba_bersih / jumlah_saham if jumlah_saham > 0 else 0
    bvps = total_ekuitas / jumlah_saham if jumlah_saham > 0 else 0
    
    # --- VALUASI RELATIF ---
    per = harga_pasar / eps if eps != 0 else 0
    pbv = harga_pasar / bvps if bvps != 0 else 0
    
    # --- VALUASI ABSOLUT (DCF) ---
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
    
    # --- MARGIN OF SAFETY (MoS) ---
    mos = ((nilai_intrinsik - harga_pasar) / nilai_intrinsik) * 100 if nilai_intrinsik > 0 else 0
    is_sehat = (data_mentah['net_cfo_juta'] > 0) and (data_mentah['net_cfi_juta'] < 0)
    
    return {
        "eps": eps, "bvps": bvps, "per": per, "pbv": pbv,
        "nilai_intrinsik": nilai_intrinsik, "mos": mos,
        "projected_income": projected_income,
        "discounted_income": discounted_income,
        "terminal_value": terminal_value,
        "discounted_tv": discounted_tv,
        "total_valuasi_juta": total_valuasi_juta,
        "is_sehat": is_sehat
    }