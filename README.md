# Diagnosis Kondisi Lahan Cabai dari Data Sensor IoT (Forward Chaining)

| Informasi Mahasiswa | |
|---|---|
| **Nama** | NI PUTU AYU DIAN SULASTRI |
| **NIM** | F1D02510021 |
| **Mata Kuliah** | Kecerdasan Buatan |
| **Topik Proyek** | Sistem Pakar Diagnosis Kondisi Lahan Cabai Merah Berbasis Sensor IoT |

---

## 1. Topik dan Cara Menjalankan Program
Sistem pakar sederhana untuk *smart agriculture*: program membaca data parameter fisik lahan cabai (kelembapan tanah, pH tanah, suhu udara, kelembapan udara) serta observasi visual lapangan petani, lalu menyimpulkan diagnosis gangguan lahan beserta **rekomendasi tindakan solutif** dan **pohon alasan** (aturan mana saja yang terpicu). Mesin forward chaining dibangun sendiri tanpa library sistem pakar eksternal.

- **Bahasa Pemrograman:** Python 3.10+ (diuji pada Python 3.12)
- **Ketergantungan Library:** Hanya menggunakan *standard library* bawaan (`json`, `argparse`, `textwrap`, `operator`, `os`, `sys`).

### Perintah Menjalankan Program:
1. **Mode Interaktif (Tanya-Jawab Terminal):**
   ```bash
   python main.py
   ```
2. **Mode Baca Data Sensor IoT (File Kasus JSON):**
   ```bash
   python main.py --file kasus/kasus1.json
   ```
3. **Mencetak Tabel Aturan IF-THEN:**
   ```bash
   python main.py --tabel
   ```
4. **Menjalankan Pengujian Unit Otomatis:**
   ```bash
   python test_cabai.py
   ```

---

## 2. Daftar Sumber dan Tabel Aturan

### A. Daftar Sumber Rujukan
| Kode | Judul & Penulis | Penerbit / Jurnal | Tautan (URL / DOI) | Tanggal Akses |
|:---:|---|---|:---:|:---:|
| **S1** | *Evaluasi Paket Teknologi Budidaya Hibrida Cabai Merah untuk Hasil Tinggi di Lahan Masam* <br>— Syukur, M., Sujiprihati, S., & Koswara, J. (2021) | Jurnal Hortikultura Indonesia (Departemen Agronomi & Hortikultura IPB University), Vol. 12 No. 1, hal. 21–30 | [DOI: 10.29244/jhi.12.1.21-30](https://doi.org/10.29244/jhi.12.1.21-30) <br>(Akses: [journal.ipb.ac.id](https://journal.ipb.ac.id/index.php/jhi/article/view/33420)) | 13 November 2026 |
| **S2** | *Penerapan IoT untuk Monitoring Suhu dan Kelembaban pada Tanaman Cabai* <br>— Wicaksono, M.F. & Syahrin, A. (2022) | Jurnal ELKOMIKA (Institut Teknologi Nasional Bandung), Vol. 10 No. 3, hal. 568–578 | [DOI: 10.26760/elkomika.v10i3.568](https://doi.org/10.26760/elkomika.v10i3.568) <br>(Akses: [ejurnal.itenas.ac.id](https://ejurnal.itenas.ac.id/index.php/elkomika/article/view/568)) | 13 November 2026 |

### B. Konversi Nilai Numerik Sensor ke Fakta
| Sensor | Ambang Batas | Fakta yang Dihasilkan | Dasar Penentuan Ambang |
|---|:---:|---|---|
| Kelembapan tanah | `< 40%` / `> 80%` | `tanah kering` / `tanah terlalu basah` | Kalibrasi batas kenyamanan perakaran cabai (asumsi proyek IoT) |
| pH tanah | `< 5,5` / `> 7,0` | `pH tanah di bawah 5,5` / `pH tanah di atas 7,0` | S1 hal. 23 (toleransi optimal cabai 5,5–7,0; <5,5 masam, >7,0 basa) |
| Suhu udara | `> 35°C` / `< 15°C` | `suhu udara di atas 35°C` / `suhu udara di bawah 15°C` | S2 hal. 570 (stres panas memicu bunga rontok, suhu dingin hambat vegetatif) |
| Kelembapan udara | `> 85%` | `kelembapan udara tinggi` | S2 hal. 571 (kelembapan optimal 60–80%; >85% kondusif bagi spora jamur) |

### C. Tabel Aturan IF-THEN
| Aturan | Premis (IF) | Mode | Konklusi (THEN) | Sumber |
|:---:|---|:---:|---|:---:|
| **R1** | tanah kering, hujan tidak turun beberapa hari terakhir | DAN | tanaman kekurangan air | S1 |
| **R2** | tanah terlalu basah, air menggenang di bedengan atau drainase buruk | ATAU | tanah becek | S1 |
| **R3** | tanah becek, sedang musim hujan | DAN | lingkungan mendukung penyakit tular air | S1 |
| **R4** | lingkungan mendukung penyakit tular air, kelembapan udara tinggi | ATAU | risiko penyakit jamur | S1, S2 |
| **R5** | risiko penyakit jamur, daun layu mulai dari bawah dan menguning | DAN | dugaan penyakit layu | S1 |
| **R6** | pH tanah di bawah 5,5, pH tanah di atas 7,0 | ATAU | pH tanah di luar kisaran sesuai | S1, S2 |
| **R7** | pH tanah di luar kisaran sesuai | DAN | serapan hara terganggu | S1, S2 |
| **R8** | serapan hara terganggu, pH tanah di bawah 5,5 | DAN | tindakan: lakukan pengapuran dolomit | S1 |
| **R9** | serapan hara terganggu, pH tanah di atas 7,0 | DAN | fosfor tertahan karena terfiksasi Ca dan Mg | S1 |
| **R10** | tanaman kekurangan air | DAN | tindakan: lakukan penyiraman | S1 |
| **R11** | tanah becek | DAN | tindakan: kurangi penyiraman dan perbaiki drainase bedengan | S1 |
| **R12** | risiko penyakit jamur | DAN | tindakan: bersihkan lahan (sanitasi) dan beri Trichoderma | S1 |
| **R13** | dugaan penyakit layu | DAN | tindakan: cabut dan musnahkan tanaman terserang | S1 |
| **R14** | suhu udara di atas 35°C | DAN | risiko bunga gugur dan gagal berbuah (stres panas) | S2 |
| **R15** | suhu udara di bawah 15°C | DAN | pertumbuhan vegetatif terganggu (suhu rendah) | S2 |

> **Rantai Inferensi (*Chaining*):** R2 (`tanah becek`) $\rightarrow$ R3 (`lingkungan mendukung penyakit tular air`) $\rightarrow$ R4 (`risiko penyakit jamur`) $\rightarrow$ R5 (`dugaan penyakit layu`) $\rightarrow$ R13 (`tindakan: cabut dan musnahkan tanaman terserang`).

---

## 3. Metode Inferensi: Forward Chaining
Metode yang dipilih adalah **Forward Chaining** (pelacakan maju), yaitu metode penalaran berbasis data (*data-driven*) yang bermula dari sekumpulan fakta yang ada (pembacaan sensor IoT dan jawaban observasi visual) lalu secara bertahap mencocokkan aturan (*production rules*) untuk menghasilkan kesimpulan baru hingga mencapai rekomendasi tindakan.

### Alasan Pemilihan Metode:
1. **Alur Alami Berbasis Data (*Bottom-Up*):** Pada sistem monitoring lahan dengan IoT, data numerik sensor (suhu, kelembapan, pH) terus-menerus masuk sebagai fakta awal. Sistem secara alami bergerak maju dari data ke diagnosis tanpa harus menebak hipotesis akhir terlebih dahulu.
2. **Kesesuaian Rantai Sebab-Akibat Pertanian:** Gangguan tanaman memiliki sifat kausalitas berantai. Misalnya genangan air memicu kebecekan, kebecekan memicu jamur, dan jamur memicu layu. Forward chaining sangat efisien mengevaluasi rantai ini secara beruntun.
3. **Transparansi Penelusuran Alasan (*Explainability*):** Petani memerlukan kepastian alasan di balik sebuah rekomendasi. Forward chaining mempermudah pembuatan pohon eksplanasi aturan mana saja yang dieksekusi.

### Alur Kerja Algoritma:
1. Konversi angka sensor menjadi fakta simbolik melalui batas ambang.
2. Simpan seluruh fakta sensor dan observasi ke dalam `memori` kerja (*working memory*).
3. Cari seluruh aturan yang premisnya terpenuhi dan kesimpulannya belum ada di memori.
4. Pilih aturan pertama yang cocok, tambahkan kesimpulannya ke `memori`, dan catat relasi aturan pada graf pelacakan alasan.
5. Ulangi proses hingga tidak ada lagi aturan baru yang dapat dibangkitkan (*stopping condition*).

---

## 4. Kasus Uji dan Hasil Evaluasi

Berikut pengujian sistem terhadap 4 skenario kasus uji (mencakup kasus positif sederhana, kasus negatif/normal, kasus berantai panjang, dan kasus kombinasi pH basa):

### Kasus 1: Kekurangan Air & Tindakan Penyiraman (Kasus Positif)
- **Tujuan:** Menguji aturan dasar kondisi tanah kering tanpa hujan.
- **Masukan:** Kelembapan tanah: `30%`, pH: `6.3`, Suhu: `30°C`, RH: `70%`, Pengamatan: *"hujan tidak turun beberapa hari terakhir"*.
- **Kesimpulan yang Dihasilkan:** `tanaman kekurangan air` $\rightarrow$ `tindakan: lakukan penyiraman`.
- **Tangkapan Layar:**
  ![Kasus 1](screenshot/kasus1.jpeg)

---

### Kasus 2: Semua Kondisi Lahan Normal (Kasus Negatif)
- **Tujuan:** Menguji ketepatan sistem agar tidak memberikan kesimpulan salah saat seluruh parameter normal.
- **Masukan:** Kelembapan tanah: `60%`, pH: `6.4`, Suhu: `28°C`, RH: `75%`, Pengamatan: *(tidak ada)*.
- **Kesimpulan yang Dihasilkan:** *Tidak ada masalah yang bisa disimpulkan dari data Anda (kondisi normal).*
- **Tangkapan Layar:**
  ![Kasus 2](screenshot/kasus2.jpeg)

---

### Kasus 3: Rantai Kompleks Multi-Masalah (Kasus Positif Berantai)
- **Tujuan:** Menguji inferensi berantai panjang (*multi-hop chaining*) melibatkan drainase buruk, jamur, layu, pH masam, dosis dolomit, dan stres suhu.
- **Masukan:** Kelembapan tanah: `85%`, pH: `5.0`, Suhu: `36°C`, RH: `90%`, Pengamatan: *"sedang musim hujan"*, *"air menggenang di bedengan atau drainase buruk"*, *"daun layu mulai dari bawah dan menguning"*.
- **Kesimpulan yang Dihasilkan:**
  1. Diagnosis: `tanah becek`, `lingkungan mendukung penyakit tular air`, `risiko penyakit jamur`, `dugaan penyakit layu`, `pH tanah di luar kisaran sesuai`, `serapan hara terganggu`, `risiko bunga gugur dan gagal berbuah (stres panas)`.
  2. Tindakan: Lakukan pengapuran dolomit (rekomendasi: pH 5.0 $\rightarrow$ 7.8 ton/ha atau 78 kg/100m²), kurangi penyiraman & perbaiki drainase, bersihkan lahan & beri Trichoderma, cabut dan musnahkan tanaman terserang.
- **Tangkapan Layar:**
  ![Kasus 3](screenshot/kasus3.jpeg)

---

### Kasus 4: pH Tanah Terlalu Tinggi & Suhu Dingin (Kasus Positif)
- **Tujuan:** Menguji aturan fiksasi fosfor akibat pH basa dan hambatan vegetatif akibat suhu rendah.
- **Masukan:** Kelembapan tanah: `55%`, pH: `7.4`, Suhu: `12°C`, RH: `70%`, Pengamatan: *(tidak ada)*.
- **Kesimpulan yang Dihasilkan:** `fosfor tertahan karena terfiksasi Ca dan Mg`, `pertumbuhan vegetatif terganggu (suhu rendah)`.
- **Tangkapan Layar:**
  ![Kasus 4](screenshot/kasus4.jpeg)

---

## 5. Batas Keberlakuan
Basis pengetahuan sistem ini bersumber dari kajian agronomi budidaya cabai merah di lahan masam pada *Jurnal Hortikultura Indonesia* IPB (2021) serta penerapan sistem monitoring iklim mikro lahan cabai berbasis IoT pada *Jurnal ELKOMIKA* (2022). Sistem ini ditujukan khusus untuk tanaman cabai merah (*Capsicum annuum L.*) pada lahan terbuka di wilayah beriklim tropis Indonesia. Ambang batas kelembapan tanah merupakan kalibrasi sensor (asumsi teknis proyek) dan perlu disesuaikan kembali dengan karakteristik tekstur tanah setempat (misal: tanah lempung berliat vs tanah pasir). Hasil diagnosis dan anjuran tindakan merupakan rekomendasi awal (*early warning support*) untuk membantu monitoring lahan, bukan vonis mutlak pengganti uji laboratorium tanah atau bimbingan penyuluh pertanian lapangan (PPL).

---

## 6. Penggunaan Alat Bantu AI
Sesuai dengan ketentuan pedoman tugas, AI digunakan sebagai alat bantu belajar dan eksplorasi teknis:
1. **Peran AI:** Bantuan AI (Google Antigravity / Gemini) digunakan dalam penyusunan struktur kerangka kode Python (*boilerplate* algoritma forward chaining di `engine.py`), penataan skema data `kb_cabai.json`, serta perapian tata letak tampilan teks output terminal (*justified text wrapping*).
2. **Kontribusi Mandiri:** Mahasiswa melakukan penelusuran mandiri terhadap literatur ilmiah (jurnal IPB dan jurnal ELKOMIKA), merumuskan 15 relasi sebab-akibat aturan IF-THEN beserta ambang batas sensor, merancang skenario pengujian kasus uji (kasus 1–4), serta mempelajari dan memahami sepenuhnya setiap alur baris kode inferensi yang dieksekusi.
