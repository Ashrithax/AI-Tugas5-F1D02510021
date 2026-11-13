"""Tes otomatis. Jalankan: python test_cabai.py  (atau: pytest)"""
from engine import muat_kb, forward_chaining
from sensor import angka_ke_fakta

KB = muat_kb()


def kesimpulan(bacaan, ya=()):
    """Jalankan seluruh alur (angka -> fakta -> FC) lalu kembalikan semua kesimpulan."""
    fakta_sensor, _ = angka_ke_fakta(KB, bacaan)
    _, asal, _ = forward_chaining(KB, fakta_sensor + list(ya))
    return set(asal)


def test_kasus1_kekurangan_air():
    h = kesimpulan({"kelembapan_tanah": 30, "ph_tanah": 6.3, "suhu_udara": 30, "kelembapan_udara": 70},
                   ["hujan tidak turun beberapa hari terakhir"])
    assert "tanaman kekurangan air" in h
    assert "tindakan: lakukan penyiraman" in h


def test_kasus2_negatif():
    h = kesimpulan({"kelembapan_tanah": 60, "ph_tanah": 6.4, "suhu_udara": 28, "kelembapan_udara": 75})
    assert h == set()


def test_kasus3_rantai_panjang():
    h = kesimpulan({"kelembapan_tanah": 85, "ph_tanah": 5.0, "suhu_udara": 36, "kelembapan_udara": 90},
                   ["sedang musim hujan", "air menggenang di bedengan atau drainase buruk",
                    "daun layu mulai dari bawah dan menguning"])
    assert {"tanah becek", "lingkungan mendukung penyakit tular air", "risiko penyakit jamur",
            "dugaan penyakit layu", "serapan hara terganggu",
            "tindakan: lakukan pengapuran dolomit",
            "tindakan: cabut dan musnahkan tanaman terserang",
            "risiko bunga gugur dan gagal berbuah (stres panas)"} <= h


def test_kasus4_ph_tinggi_dan_dingin():
    h = kesimpulan({"kelembapan_tanah": 55, "ph_tanah": 7.4, "suhu_udara": 12, "kelembapan_udara": 70})
    assert "fosfor tertahan karena terfiksasi Ca dan Mg" in h
    assert "pertumbuhan vegetatif terganggu (suhu rendah)" in h


def test_tanah_kering_tapi_hujan_turun_tidak_disiram():
    # tanah kering saja (tanpa 'hujan tidak turun') tidak boleh memicu penyiraman
    h = kesimpulan({"kelembapan_tanah": 30, "ph_tanah": 6.3, "suhu_udara": 30, "kelembapan_udara": 70})
    assert "tindakan: lakukan penyiraman" not in h


def test_semua_aturan_punya_sumber_valid():
    for r in KB["aturan"]:
        for k in r["sumber"].split(","):
            assert k.strip() in KB["sumber"], f"{r['id']} menunjuk sumber {k} yang tidak ada"


def test_ada_rantai_aturan():
    hasil = {r["maka"] for r in KB["aturan"]}
    assert any(s in hasil for r in KB["aturan"] for s in r["jika"])


if __name__ == "__main__":
    for nama, fungsi in list(globals().items()):
        if nama.startswith("test_"):
            fungsi()
            print("lulus:", nama)
