import argparse
import json
import os
import sys
import textwrap

from engine import muat_kb, forward_chaining, cari_alasan
from sensor import angka_ke_fakta

LEBAR = 66
try:
    sys.stdout.reconfigure(encoding="utf-8")   
except Exception:
    pass

PAKAI_WARNA = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def warna(teks, kode):
    return f"\033[{kode}m{teks}\033[0m" if PAKAI_WARNA else teks


def judul(teks):
    print()
    print(warna(teks, "1;36"))
    print(warna("-" * LEBAR, "36"))


def ratakan_kiri_kanan(teks, lebar=LEBAR, indent="", sub_indent=""):
    kata_kata = teks.split()
    if not kata_kata:
        return ""
    baris_baris, baris_ini, panjang_ini = [], [], 0
    lebar_target = lebar - len(indent)
    for kata in kata_kata:
        if baris_ini and (panjang_ini + len(kata) + len(baris_ini) > lebar_target):
            baris_baris.append(baris_ini)
            baris_ini = [kata]
            panjang_ini = len(kata)
            lebar_target = lebar - len(sub_indent)
        else:
            baris_ini.append(kata)
            panjang_ini += len(kata)
    if baris_ini:
        baris_baris.append(baris_ini)

    hasil = []
    for i, b in enumerate(baris_baris):
        pref = indent if i == 0 else sub_indent
        lebar_aktif = lebar - len(pref)
        total_karakter = sum(len(k) for k in b)
        jumlah_celah = len(b) - 1
        total_spasi = lebar_aktif - total_karakter
        if (i == len(baris_baris) - 1 or jumlah_celah < 1 or 
                total_spasi > jumlah_celah * 4 or total_karakter >= lebar_aktif):
            hasil.append(pref + " ".join(b))
        else:
            spasi_dasar = total_spasi // jumlah_celah
            sisa = total_spasi % jumlah_celah
            baris_str = ""
            for j in range(jumlah_celah):
                baris_str += b[j] + (" " * (spasi_dasar + (1 if j < sisa else 0)))
            baris_str += b[-1]
            hasil.append(pref + baris_str)
    return "\n".join(hasil)

def tanya_angka(sensor):
    satuan = f" ({sensor['satuan']})" if sensor["satuan"] else ""
    while True:
        teks = input(f"  {sensor['label']}{satuan} > ").strip().replace(",", ".")
        try:
            nilai = float(teks)
        except ValueError:
            print("    Masukkan angka saja, contoh: 6.5")
            continue
        if sensor["min"] <= nilai <= sensor["maks"]:
            return nilai
        print(f"    Nilai harus antara {sensor['min']:g} dan {sensor['maks']:g}.")

def tanya_ya_tidak(pertanyaan):
    while True:
        jawab = input(f"  {pertanyaan} (y/t) > ").strip().lower()
        if jawab in ("y", "t"):
            return jawab == "y"
        print("    Jawab dengan y atau t.")

def baca_interaktif(kb):
    print("\nMasukkan data sensor lahan cabai Anda:")
    bacaan = {s["kunci"]: tanya_angka(s) for s in kb["sensor"]}
    print("\nJawab pertanyaan pengamatan (y = ya, t = tidak):")
    fakta_ya = [p["fakta"] for p in kb["pertanyaan"] if tanya_ya_tidak(p["tanya"])]
    return bacaan, fakta_ya


def baca_file(path, kb):
    target_path = path
    if not os.path.exists(target_path):
        alt_path = os.path.join("kasus", path)
        if os.path.exists(alt_path):
            target_path = alt_path
        elif path.startswith("kasus/") or path.startswith("kasus\\"):
            stripped = os.path.basename(path)
            if os.path.exists(stripped):
                target_path = stripped

    with open(target_path, encoding="utf-8") as f:
        data = json.load(f)
    bacaan = data.get("sensor", {})
    fakta_ya = data.get("ya", [])
    dikenal = {p["fakta"] for p in kb["pertanyaan"]}
    for f_ in fakta_ya:
        if f_ not in dikenal:
            print(warna(f"Peringatan: fakta '{f_}' tidak ada di daftar pertanyaan.", "33"))
    return bacaan, fakta_ya

def saran_dolomit(kb, ph):
    baris = min(kb["dolomit"]["tabel"], key=lambda b: abs(b["ph"] - ph))
    kg_100m2 = baris["ton_per_ha"] * 10     
    return (f"Acuan dosis dolomit: pH {baris['ph']:g} -> {baris['ton_per_ha']:g} ton/ha "
            f"(sekitar {kg_100m2:g} kg per 100 m2). Baris tabel terdekat dengan pH {ph:g}; "
            f"[{kb['dolomit']['sumber']}]")

def tampilkan_hasil(kb, bacaan, jejak, fakta_ya, fakta_awal, memori, asal, urutan):
    print()
    print(warna("=" * LEBAR, "1;32"))
    print(warna(kb["judul"].upper().center(LEBAR), "1;32"))
    print(warna("Metode: Forward Chaining".center(LEBAR), "32"))
    print(warna("=" * LEBAR, "1;32"))

    judul("1. DATA MASUKAN")
    for s in kb["sensor"]:
        if s["kunci"] in bacaan:
            val = f"{bacaan[s['kunci']]:g} {s['satuan']}".strip()
            print(f"  {s['label']:<18}: {val}")
    if fakta_ya:
        lbl_ya = "  Pengamatan 'ya'   : "
        print(ratakan_kiri_kanan(", ".join(fakta_ya), LEBAR, indent=lbl_ya, sub_indent=" " * len(lbl_ya)))
    else:
        print("  Pengamatan 'ya'   : (tidak ada)")

    judul("2. FAKTA DARI SENSOR (angka -> fakta)")
    for baris in jejak or ["(semua angka sensor dalam batas normal)"]:
        print(textwrap.fill(f"  - {baris}", width=LEBAR, subsequent_indent="    "))

    judul("3. PROSES FORWARD CHAINING")
    if fakta_awal:
        lbl_fa = "  Fakta awal        : "
        print(ratakan_kiri_kanan(", ".join(fakta_awal), LEBAR, indent=lbl_fa, sub_indent=" " * len(lbl_fa)))
    else:
        print("  Fakta awal        : (tidak ada)")
    for i, r in enumerate(urutan, 1):
        teks_siklus = f"  Siklus {i:<2}: {r['id']} -> {r['maka']}"
        print(textwrap.fill(teks_siklus, width=LEBAR, subsequent_indent="             "))
    print(f"  Siklus {len(urutan) + 1:<2}: tidak ada aturan baru, berhenti")

    hasil = [r["maka"] for r in urutan]
    tindakan = [h for h in hasil if h.startswith("tindakan:")]
    diagnosis = [h for h in hasil if not h.startswith("tindakan:")]

    judul("4. KESIMPULAN")
    if not hasil:
        print(warna("  Tidak ada masalah yang bisa disimpulkan dari data Anda.", "32"))
        print("  Kondisi lahan tampak sesuai menurut aturan yang tersedia.")
    else:
        print(warna("  Diagnosis:", "1"))
        for d in diagnosis:
            print(warna(textwrap.fill(f"   * {d}", width=LEBAR, subsequent_indent="     "), "33"))
        if tindakan:
            print(warna("  Tindakan yang disarankan:", "1"))
            for n, t in enumerate(tindakan, 1):
                isi = t.replace("tindakan: ", "")
                teks_tindakan = f"   {n}. {isi[0].upper() + isi[1:]}"
                print(warna(textwrap.fill(teks_tindakan, width=LEBAR, subsequent_indent="      "), "32"))
                if t == "tindakan: lakukan pengapuran dolomit":
                    if bacaan.get("ph_tanah") is not None:
                        saran = saran_dolomit(kb, bacaan["ph_tanah"])
                        print(warna(ratakan_kiri_kanan(f"-> {saran}", LEBAR, indent="      ", sub_indent="         "), "36"))
                    else:
                        print("      -> (Data pH tanah tidak tersedia untuk menghitung dosis dolomit spesifik)")

        judul("5. ALASAN (aturan mana yang dipakai)")
        dipakai = {s for r in urutan for s in r["jika"]}
        for h in [x for x in hasil if x not in dipakai]:
            for baris_alasan in cari_alasan(h, asal, memori):
                spasi_awal = len(baris_alasan) - len(baris_alasan.lstrip())
                print(textwrap.fill(baris_alasan, width=LEBAR, subsequent_indent=" " * (spasi_awal + 4)))

        judul("6. SUMBER")
        kode = sorted({k.strip() for r in urutan for k in r["sumber"].split(",")})
        for k in kode:
            teks_sumber = f"{k}: {kb['sumber'][k]}"
            print(ratakan_kiri_kanan(teks_sumber, LEBAR, indent="  ", sub_indent="     "))

    judul("CATATAN BATAS KEBERLAKUAN")
    print(ratakan_kiri_kanan(kb["batas"], LEBAR, indent="  ", sub_indent="  "))
    print()


def cetak_tabel(kb):
    print("| Aturan | IF | THEN | Sumber |")
    print("|---|---|---|---|")
    for r in kb["aturan"]:
        sambung = f" {r['mode'].upper()} "
        print(f"| {r['id']} | {sambung.join(r['jika'])} | {r['maka']} | {r['sumber']} |")


def main():
    parser = argparse.ArgumentParser(description="Diagnosis lahan cabai (Forward Chaining)")
    parser.add_argument("--file", help="baca data dari file JSON (contoh: kasus/kasus1.json)")
    parser.add_argument("--kb", default="kb_cabai.json", help="file aturan (default: kb_cabai.json)")
    parser.add_argument("--tabel", action="store_true", help="cetak tabel aturan dalam format Markdown")
    args = parser.parse_args()

    kb = muat_kb(args.kb)
    if args.tabel:
        cetak_tabel(kb)
        return

    bacaan, fakta_ya = baca_file(args.file, kb) if args.file else baca_interaktif(kb)

    fakta_sensor, jejak = angka_ke_fakta(kb, bacaan)     
    fakta_awal = fakta_sensor + fakta_ya
    memori, asal, urutan = forward_chaining(kb, fakta_awal)   
    tampilkan_hasil(kb, bacaan, jejak, fakta_ya, fakta_awal, memori, asal, urutan)


if __name__ == "__main__":
    main()
