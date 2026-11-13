"""
sensor.py - Mengubah ANGKA sensor menjadi FAKTA yang dimengerti mesin FC.

Contoh: pH tanah = 5.0  ->  fakta "pH tanah di bawah 5,5"
Batas-batasnya ada di bagian "ambang" pada kb_cabai.json (bukan ditulis di kode),
jadi kalau ingin mengubah ambang, cukup edit file JSON.
"""
import operator

PEMBANDING = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
}


def angka_ke_fakta(kb, bacaan):
    """bacaan = {"ph_tanah": 5.0, ...}. Mengembalikan (daftar_fakta, daftar_jejak)."""
    label = {s["kunci"]: s["label"] for s in kb["sensor"]}
    fakta, jejak = [], []

    for a in kb["ambang"]:
        nilai = bacaan.get(a["kunci"])
        if nilai is None:          # sensor ini tidak dibaca -> lewati
            continue
        if PEMBANDING[a["operator"]](nilai, a["batas"]):
            fakta.append(a["fakta"])
            jejak.append(
                f"{label[a['kunci']]} {nilai:g} {a['operator']} {a['batas']:g}"
                f"  ->  {a['fakta']}  [{a['sumber']}]"
            )
    return fakta, jejak
