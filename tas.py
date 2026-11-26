import json
import os
from datetime import datetime

pendo 
DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def _path(nama_file):
    return os.path.join(DATA_DIR, nama_file)


def muat_data(nama_file):
    """Membaca data (berupa list) dari file JSON.

    Jika file belum ada, mengembalikan list kosong.
    Jika file rusak, file diamankan dengan akhiran .rusak lalu mengembalikan list kosong.
    """
    path = _path(nama_file)
    try:
        with open(path, "r", encoding="utf-8") as berkas:
            data = json.load(berkas)
        if not isinstance(data, list):
            raise ValueError("isi file harus berupa list")
        return data
    except FileNotFoundError:
        return []
    except ValueError as galat:  
        print(f"[!] File '{nama_file}' rusak ({galat}).")
        try:
            os.replace(path, path + ".rusak")
            print(f"    File lama diamankan sebagai '{nama_file}.rusak'.")
        except OSError:
            pass
        return []
    except OSError as galat:
        print(f"[!] Gagal membaca file '{nama_file}': {galat}")
        return []


def simpan_data(nama_file, data):
    """Menyimpan data ke file JSON. Mengembalikan True jika berhasil."""
    path = _path(nama_file)
    sementara = path + ".tmp"
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(sementara, "w", encoding="utf-8") as berkas:
            json.dump(data, berkas, indent=4, ensure_ascii=False)
        os.replace(sementara, path)
        return True
    except OSError as galat:
        print(f"[!] Gagal menyimpan data ke '{nama_file}': {galat}")
        return False


def input_teks(prompt, boleh_kosong=False):
    """Meminta teks. Jika tidak boleh kosong, akan diulang sampai diisi."""
    while True:
        nilai = input(prompt).strip()
        if nilai != "" or boleh_kosong:
            return nilai
        print("  [!] Input tidak boleh kosong.")


def input_angka(prompt, minimum=None, boleh_kosong=False, pesan_min=None):
    """Meminta bilangan bulat.

    - minimum      : nilai terkecil yang diperbolehkan (None = bebas)
    - boleh_kosong : jika True dan pengguna menekan Enter, mengembalikan None
    - pesan_min    : pesan khusus bila nilai kurang dari minimum
    """
    while True:
        teks = input(prompt).strip()
        if teks == "" and boleh_kosong:
            return None
        try:
            nilai = int(teks)
        except ValueError:
            print("  [!] Input harus berupa angka bulat (contoh: 15000).")
            continue
        if minimum is not None and nilai < minimum:
            if pesan_min:
                print(f"  [!] {pesan_min}")
            else:
                print(f"  [!] Nilai minimal adalah {minimum}.")
            continue
        return nilai


def input_pilihan(prompt, pilihan_valid):
    """Meminta salah satu pilihan dari kumpulan pilihan_valid (set/tuple/list string)."""
    while True:
        nilai = input(prompt).strip()
        if nilai in pilihan_valid:
            return nilai
        print("  [!] Pilihan tidak valid, silakan coba lagi.")


def konfirmasi(prompt):
    """Konfirmasi ya/tidak. Mengembalikan True untuk ya, False untuk tidak."""
    while True:
        jawaban = input(f"{prompt} (y/n): ").strip().lower()
        if jawaban in ("y", "ya"):
            return True
        if jawaban in ("n", "t", "tidak"):
            return False
        print("  [!] Jawab dengan 'y' atau 'n'.")


LEBAR = 70


def garis(karakter="="):
    print(karakter * LEBAR)


def judul(teks):
    print()
    garis("=")
    print(teks.center(LEBAR))
    garis("=")


def format_rupiah(angka):
    """Contoh: 15000 -> Rp15.000"""
    return "Rp" + f"{angka:,}".replace(",", ".")


def cetak_tabel_menu(daftar_menu):
    """Mencetak tabel menu dari list of dict."""
    print(f"{'ID':<5}{'Nama':<27}{'Kategori':<11}{'Harga':>12}  Status")
    garis("-")
    for item in daftar_menu:
        status = "Tersedia" if item["tersedia"] else "Tidak tersedia"
        print(
            f"{item['id']:<5}{item['nama']:<27}{item['kategori']:<11}"
            f"{format_rupiah(item['harga']):>12}  {status}"
        )


FILE_MENU = "menu.json"
KATEGORI = ("Makanan", "Minuman")  
MAKS_NAMA = 25
KUNCI_WAJIB = {"id", "nama", "kategori", "harga", "tersedia"}  


def _item_valid(item):
    """Memeriksa apakah satu data menu dari file memiliki struktur yang benar."""
    return (
        isinstance(item, dict)
        and KUNCI_WAJIB <= item.keys()
        and isinstance(item["id"], int)
        and isinstance(item["nama"], str)
        and item["kategori"] in KATEGORI
        and isinstance(item["harga"], int)
        and item["harga"] > 0
        and isinstance(item["tersedia"], bool)
    )


def muat_menu():
    """Membaca data menu dari file. Data yang strukturnya salah diabaikan."""
    data = muat_data(FILE_MENU)
    daftar_menu = [item for item in data if _item_valid(item)]
    diabaikan = len(data) - len(daftar_menu)
    if diabaikan > 0:
        print(f"[!] {diabaikan} data menu tidak valid diabaikan saat membaca file.")
    return daftar_menu


def simpan_menu(daftar_menu):
    return simpan_data(FILE_MENU, daftar_menu)


def cari_menu(daftar_menu, id_menu):
    """Mencari menu berdasarkan ID. Mengembalikan dict atau None."""
    for item in daftar_menu:
        if item["id"] == id_menu:
            return item
    return None


def _id_baru(daftar_menu):
    return max((item["id"] for item in daftar_menu), default=0) + 1


def _nama_sudah_ada(daftar_menu, nama, abaikan_id=None):
    nama_terdaftar = {item["nama"].lower() for item in daftar_menu if item["id"] != abaikan_id}
    return nama.lower() in nama_terdaftar


def _input_nama(daftar_menu, nama_lama=None, abaikan_id=None):
    while True:
        if nama_lama is None:
            nama = input_teks("Nama menu              : ")
        else:
            nama = input_teks(f"Nama menu [{nama_lama}]: ", boleh_kosong=True)
            if nama == "":
                return nama_lama
        if len(nama) > MAKS_NAMA:
            print(f"  [!] Nama menu maksimal {MAKS_NAMA} karakter.")
        elif _nama_sudah_ada(daftar_menu, nama, abaikan_id):
            print("  [!] Nama menu sudah digunakan, gunakan nama lain.")
        else:
            return nama


def _input_kategori(kategori_lama=None):
    for nomor, kategori in enumerate(KATEGORI, start=1):
        print(f"  {nomor}. {kategori}")
    pilihan_valid = {str(nomor) for nomor in range(1, len(KATEGORI) + 1)}
    akhiran = ": "
    if kategori_lama is not None:
        pilihan_valid.add("")
        akhiran = f" [Enter = tetap '{kategori_lama}']: "
    pilihan = input_pilihan("Pilih kategori" + akhiran, pilihan_valid)
    if pilihan == "":
        return kategori_lama
    return KATEGORI[int(pilihan) - 1]


def _input_harga(harga_lama=None):
    pesan = "Harga harus berupa angka positif (lebih dari 0)."
    if harga_lama is None:
        return input_angka("Harga (Rp)             : ", minimum=1, pesan_min=pesan)
    harga = input_angka(
        f"Harga (Rp) [{harga_lama}]: ", minimum=1, boleh_kosong=True, pesan_min=pesan
    )
    return harga_lama if harga is None else harga


def _pilih_id(daftar_menu, aksi):
    """Meminta ID menu. Mengembalikan dict menu, atau None jika dibatalkan/tidak ditemukan."""
    id_menu = input_angka(f"Masukkan ID menu yang {aksi} (0 = batal): ", minimum=0)
    if id_menu == 0:
        print("Dibatalkan.")
        return None
    item = cari_menu(daftar_menu, id_menu)
    if item is None:
        print("  [!] Menu dengan ID tersebut tidak ditemukan.")
    return item


def cetak_daftar_menu(daftar_menu):
    """Mencetak tabel menu (tanpa judul). Menampilkan pesan bila kosong."""
    if not daftar_menu:
        print("Belum ada data menu.")
    else:
        cetak_tabel_menu(daftar_menu)


def tambah_menu(daftar_menu):
    judul("TAMBAH MENU")
    nama = _input_nama(daftar_menu)
    kategori = _input_kategori()
    harga = _input_harga()
    daftar_menu.append(
        {
            "id": _id_baru(daftar_menu),
            "nama": nama,
            "kategori": kategori,
            "harga": harga,
            "tersedia": True,
        }
    )
    if simpan_menu(daftar_menu):
        print(f"Menu '{nama}' berhasil ditambahkan.")


def tampilkan_semua_menu(daftar_menu):
    judul("DAFTAR SELURUH MENU")
    cetak_daftar_menu(daftar_menu)


def tampilkan_menu_per_kategori(daftar_menu):
    judul("DAFTAR MENU PER KATEGORI")
    if not daftar_menu:
        print("Belum ada data menu.")
        return
    for kategori in KATEGORI:
        print(f"\n>> Kategori: {kategori}")
        isi = [item for item in daftar_menu if item["kategori"] == kategori]
        if isi:
            cetak_tabel_menu(isi)
        else:
            print("   (belum ada menu pada kategori ini)")


def ubah_menu(daftar_menu):
    judul("UBAH INFORMASI MENU")
    if not daftar_menu:
        print("Belum ada data menu.")
        return
    cetak_daftar_menu(daftar_menu)
    item = _pilih_id(daftar_menu, "diubah")
    if item is None:
        return

    print("\nTekan Enter untuk mempertahankan nilai lama.")
    nama = _input_nama(daftar_menu, item["nama"], item["id"])
    kategori = _input_kategori(item["kategori"])
    harga = _input_harga(item["harga"])
    print("Status ketersediaan:\n  1. Tersedia\n  2. Tidak tersedia")
    status_lama = "Tersedia" if item["tersedia"] else "Tidak tersedia"
    pilihan = input_pilihan(f"Pilih status [Enter = tetap '{status_lama}']: ", {"", "1", "2"})
    tersedia = item["tersedia"] if pilihan == "" else (pilihan == "1")

    item["nama"] = nama
    item["kategori"] = kategori
    item["harga"] = harga
    item["tersedia"] = tersedia
    if simpan_menu(daftar_menu):
        print("Informasi menu berhasil diubah.")


def hapus_menu(daftar_menu):
    judul("HAPUS MENU")
    if not daftar_menu:
        print("Belum ada data menu.")
        return
    cetak_daftar_menu(daftar_menu)
    item = _pilih_id(daftar_menu, "dihapus")
    if item is None:
        return
    if not konfirmasi(f"Yakin hapus menu '{item['nama']}'?"):
        print("Penghapusan dibatalkan.")
        return
    daftar_menu.remove(item)
    if simpan_menu(daftar_menu):
        print(f"Menu '{item['nama']}' berhasil dihapus.")


def menu_manajemen(daftar_menu):
    """Submenu Manajemen Menu."""
    while True:
        judul("MANAJEMEN MENU")
        print("1. Tambah menu makanan/minuman")
        print("2. Tampilkan seluruh menu")
        print("3. Tampilkan menu berdasarkan kategori")
        print("4. Ubah informasi menu")
        print("5. Hapus menu")
        print("0. Kembali ke menu utama")
        pilihan = input_pilihan("Pilih menu: ", {"1", "2", "3", "4", "5", "0"})
        if pilihan == "1":
            tambah_menu(daftar_menu)
        elif pilihan == "2":
            tampilkan_semua_menu(daftar_menu)
        elif pilihan == "3":
            tampilkan_menu_per_kategori(daftar_menu)
        elif pilihan == "4":
            ubah_menu(daftar_menu)
        elif pilihan == "5":
            hapus_menu(daftar_menu)
        else:
            break


FILE_TRANSAKSI = "transaksi.json"


def muat_transaksi():
    return muat_data(FILE_TRANSAKSI)


def _buat_nomor_transaksi(daftar_transaksi):
    return f"TRX-{len(daftar_transaksi) + 1:04d}"


def hitung_subtotal(item):
    return item["harga"] * item["jumlah"]


def hitung_total(keranjang):
    total = 0
    for item in keranjang:
        total += hitung_subtotal(item)
    return total


def tampilkan_pesanan(keranjang):
    """Menampilkan isi pesanan beserta subtotal tiap item dan total pembayaran."""
    judul("DAFTAR PESANAN")
    if not keranjang:
        print("Pesanan masih kosong.")
        return
    print(f"{'No':<4}{'Nama':<27}{'Jml':>5}{'Harga':>14}{'Subtotal':>16}")
    garis("-")
    for nomor, item in enumerate(keranjang, start=1):
        print(
            f"{nomor:<4}{item['nama']:<27}{item['jumlah']:>5}"
            f"{format_rupiah(item['harga']):>14}"
            f"{format_rupiah(hitung_subtotal(item)):>16}"
        )
    garis("-")
    print(f"{'TOTAL PEMBAYARAN':<50}{format_rupiah(hitung_total(keranjang)):>16}")


def tambah_ke_pesanan(daftar_menu, keranjang):
    """Memilih menu dan memasukkan jumlah pesanan."""
    judul("PILIH MENU")
    if not daftar_menu:
        print("Belum ada menu. Tambahkan menu terlebih dahulu di Manajemen Menu.")
        return
    cetak_daftar_menu(daftar_menu)
    id_menu = input_angka("\nMasukkan ID menu yang dipesan (0 = batal): ", minimum=0)
    if id_menu == 0:
        return
    item_menu = cari_menu(daftar_menu, id_menu)
    if item_menu is None:
        print("  [!] Menu dengan ID tersebut tidak ditemukan.")
        return
    if not item_menu["tersedia"]:
        print(f"  [!] Menu '{item_menu['nama']}' sedang tidak tersedia dan tidak dapat dipesan.")
        return
    jumlah = input_angka(
        "Jumlah pesanan (minimal 1): ", minimum=1, pesan_min="Jumlah pesanan minimal 1."
    )
    # Jika menu yang sama dipesan lagi, jumlahnya digabung.
    for item in keranjang:
        if item["id"] == id_menu:
            item["jumlah"] += jumlah
            break
    else:
        keranjang.append(
            {
                "id": item_menu["id"],
                "nama": item_menu["nama"],
                "harga": item_menu["harga"],
                "jumlah": jumlah,
            }
        )
    print(f"'{item_menu['nama']}' x{jumlah} ditambahkan ke pesanan.")


def cetak_struk(transaksi):
    garis("=")
    print("STRUK TRANSAKSI KANTIN".center(LEBAR))
    garis("=")
    print(f"No. Transaksi : {transaksi['no_transaksi']}")
    print(f"Tanggal       : {transaksi['tanggal']}")
    garis("-")
    print(f"{'Nama':<27}{'Jml':>5}{'Harga':>14}{'Subtotal':>16}")
    garis("-")
    for item in transaksi["item"]:
        print(
            f"{item['nama']:<27}{item['jumlah']:>5}"
            f"{format_rupiah(item['harga']):>14}"
            f"{format_rupiah(item['subtotal']):>16}"
        )
    garis("-")
    print(f"{'Total Pembayaran':<20}: {format_rupiah(transaksi['total'])}")
    print(f"{'Uang Diterima':<20}: {format_rupiah(transaksi['uang_diterima'])}")
    print(f"{'Kembalian':<20}: {format_rupiah(transaksi['kembalian'])}")
    garis("=")
    print("Terima kasih atas kunjungan Anda!".center(LEBAR))
    garis("=")


def proses_pembayaran(keranjang, daftar_transaksi):
    """Memproses pembayaran. Mengembalikan True jika transaksi berhasil."""
    total = hitung_total(keranjang)
    judul("PEMBAYARAN")
    print(f"Total pembayaran: {format_rupiah(total)}")

    while True:
        uang = input_angka("Masukkan nominal uang pembayaran (0 = batal): ", minimum=0)
        if uang == 0:
            print("Pembayaran dibatalkan.")
            return False
        if uang < total:
            kurang = total - uang
            print(
                f"  [!] Pembayaran ditolak. Uang kurang {format_rupiah(kurang)} "
                "dari total belanja."
            )
            continue
        break

    kembalian = uang - total
    transaksi = {
        "no_transaksi": _buat_nomor_transaksi(daftar_transaksi),
        "tanggal": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "item": [
            {
                "nama": item["nama"],
                "jumlah": item["jumlah"],
                "harga": item["harga"],
                "subtotal": hitung_subtotal(item),
            }
            for item in keranjang
        ],
        "total": total,
        "uang_diterima": uang,
        "kembalian": kembalian,
    }
    daftar_transaksi.append(transaksi)
    if not simpan_data(FILE_TRANSAKSI, daftar_transaksi):
        daftar_transaksi.pop()
        print("  [!] Transaksi gagal disimpan, pembayaran dibatalkan.")
        return False

    print("\nPembayaran berhasil!\n")
    cetak_struk(transaksi)
    return True


def menu_pemesanan(daftar_menu, daftar_transaksi):
    """Submenu Pemesanan & Pembayaran untuk satu transaksi."""
    keranjang = []
    while True:
        judul("PEMESANAN")
        print("1. Pilih menu dan jumlah pesanan")
        print("2. Lihat pesanan (subtotal & total)")
        print("3. Pembayaran")
        print("0. Batalkan pesanan / kembali ke menu utama")
        pilihan = input_pilihan("Pilih menu: ", {"1", "2", "3", "0"})
        if pilihan == "1":
            tambah_ke_pesanan(daftar_menu, keranjang)
        elif pilihan == "2":
            tampilkan_pesanan(keranjang)
        elif pilihan == "3":
            if not keranjang:
                print("  [!] Pesanan masih kosong, pilih menu terlebih dahulu.")
            else:
                tampilkan_pesanan(keranjang)
                if proses_pembayaran(keranjang, daftar_transaksi):
                    return
        else:
            if keranjang and not konfirmasi("Pesanan akan dibatalkan. Lanjutkan?"):
                continue
            return


def hitung_total_pendapatan(daftar_transaksi):
    """Menjumlahkan total dari seluruh transaksi yang berhasil."""
    total = 0
    for transaksi in daftar_transaksi:
        try:
            total += transaksi["total"]
        except (KeyError, TypeError):
            print("  [!] Ada data transaksi yang rusak dan dilewati.")
    return total


def tampilkan_laporan(daftar_transaksi):
    judul("LAPORAN PENDAPATAN")
    total = hitung_total_pendapatan(daftar_transaksi)
    print(f"Total pendapatan kantin : {format_rupiah(total)}")


def main():
    data_menu = muat_menu()
    data_transaksi = muat_transaksi()

    while True:
        judul("SISTEM MANAJEMEN KANTIN DAN PEMESANAN MAKANAN")
        print("1. Manajemen Menu")
        print("2. Pemesanan")
        print("3. Laporan Pendapatan")
        print("0. Keluar")
        pilihan = input_pilihan("Pilih menu: ", {"1", "2", "3", "0"})
        if pilihan == "1":
            menu_manajemen(data_menu)
        elif pilihan == "2":
            menu_pemesanan(data_menu, data_transaksi)
        elif pilihan == "3":
            tampilkan_laporan(data_transaksi)
        else:
            print("\nTerima kasih. Data telah tersimpan.")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram dihentikan. Data yang sudah tersimpan tetap aman.")
