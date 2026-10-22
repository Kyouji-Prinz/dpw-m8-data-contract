# Praktikum Data Processing Workflow: Automated Data Contracts & Assertions

Repositori ini memuat implementasi lengkap pengujian kualitas data otomatis (**Data Contract & Assertions**) menggunakan **Pydantic v2** dan **Great Expectations (GX Core 1.x)** sesuai modul praktikum *Pertemuan 4: Automated Data Contracts & Assertions*.

---

## 1. Arsitektur & Alur Kerja Pipeline

```text
Data Producer (Order Service)
            |
            v
     Incoming Batch CSV
            |
            v
    [ DATA CONTRACT ]
   (Pydantic & GX Core)
            |
   +--------+--------+
   |                 |
  PASS              FAIL
   |                 |
   v                 v
Data Warehouse     REJECT
(warehouse_orders) (Fail-Fast: Exit 1)
```

Pipeline menerapkan prinsip **Fail-Fast**: Apabila ditemukan satu saja anomali atau data cacat dalam satu batch transaksi, seluruh batch langsung ditolak dan proses ingest dihentikan sebelum menyentuh tabel Data Warehouse.

---

## 2. Struktur Direktori Proyek

```text
pengerjaan/
├── data/
│   ├── orders_valid.csv            # Dataset transaksi valid
│   ├── orders_invalid.csv          # Dataset transaksi dengan anomali
│   ├── orders_schema_broken.csv    # Dataset dengan kolom liar (extra forbidden)
│   └── warehouse_orders.csv        # Simulasi Data Warehouse tujuan
├── src/
│   ├── contract.py                 # Definisi Data Contract model Pydantic v2
│   ├── validate_pydantic.py        # Pengujian validasi single-record (Exp 4-7)
│   ├── validate_batch.py           # Validasi batch & Quality Gate Fail-Fast (Exp 8-12)
│   └── validate_gx.py              # Suite validasi Great Expectations Core 1.x
├── data_contract_walkthrough.ipynb # Notebook interaktif seluruh percobaan
├── generate_laporan_docx.py        # Skrip otomatis generator laporan Word resmi
├── requirements.txt                # Dependensi pustaka Python
└── README.md                       # Dokumentasi proyek
```

---

## 3. Spesifikasi Data Contract

| Field | Tipe | Wajib | Aturan & Constraints |
|---|---|---|---|
| `order_id` | `str` | Ya | `min_length=1`, Identifier transaksi |
| `customer_id` | `int` | Ya | `gt=0` (harus positif) |
| `amount` | `float` | Ya | `ge=0.0` (tidak boleh negatif) |
| `status` | `Literal` | Ya | `["PAID", "PENDING", "CANCELLED"]` |
| `transaction_date` | `datetime`| Ya | Format ISO datetime |
| `payment_date` | `datetime`| Tidak | Wajib terisi jika `status == "PAID"` |
| *Extra Fields* | - | Tidak | Dilarang (`extra="forbid"`) |

---

## 4. Cara Menjalankan

### A. Validasi Single Record (Percobaan 4 - 7)
```bash
cd src
python validate_pydantic.py
```

### B. Validasi Batch & Quality Gate Fail-Fast (Percobaan 8 - 12)
```bash
cd src
# Menguji batch valid (Lolos ke warehouse)
python validate_batch.py --data ../data/orders_valid.csv

# Menguji batch invalid (Ditolak Fail-Fast)
python validate_batch.py --data ../data/orders_invalid.csv
```

### C. Validasi Great Expectations (GX Core 1.x)
```bash
cd src
python validate_gx.py --data ../data/orders_valid.csv
python validate_gx.py --data ../data/orders_invalid.csv
```
