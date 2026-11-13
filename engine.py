import json

def muat_kb(path="kb_cabai.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def syarat_terpenuhi(aturan, memori):
    ada = [syarat in memori for syarat in aturan["jika"]]
    mode = aturan.get("mode", "dan").strip().lower()
    if mode == "dan":
        return all(ada)
    elif mode == "atau":
        return any(ada)
    return False


def forward_chaining(kb, fakta_awal):
    memori = set(fakta_awal)
    asal = {}
    urutan = []

    while True:
        cocok = [
            r for r in kb["aturan"]
            if r["maka"] not in memori and syarat_terpenuhi(r, memori)
        ]
        if not cocok: break
        r = cocok[0]              
        memori.add(r["maka"])    
        asal[r["maka"]] = r        
        urutan.append(r)

    return memori, asal, urutan


def cari_alasan(hasil, asal, memori, tingkat=1):
    r = asal[hasil]
    terbukti = [s for s in r["jika"] if s in memori]
    baris = [f"{'   ' * tingkat}{hasil}  <- {r['id']} ({', '.join(terbukti)})  [{r['sumber']}]"]
    for syarat in terbukti:
        if syarat in asal:         
            baris += cari_alasan(syarat, asal, memori, tingkat + 1)
    return baris
