TOKO PINTAR POS NATIVE 2.0 -- PROYEK BARU DARI NOL
================================================

PENTING
-------
Folder ini adalah SOURCE CODE ANDROID STUDIO, BELUM BERUPA APK SIAP INSTAL.
Tidak ada APK hasil edit DEX manual di paket ini. Proyek ini dirancang agar
Android SDK resmi membuat classes.dex dan paket APK secara normal.

Mengapa proyek baru?
-------------------
APK sebelumnya mengalami kegagalan verifikasi DEX pada HP. Versi ini memiliki
package ID baru: com.tokopintar.nativepos, antarmuka Android native (bukan
WebView), SQLite lokal, dan kode Java asli.

CARA MEMBUAT APK DENGAN ANDROID STUDIO DI WINDOWS
-------------------------------------------------
1. Instal Android Studio dari https://developer.android.com/studio
2. Ekstrak ZIP ini.
3. Android Studio -> Open -> pilih folder TokoPintarNative.
4. Izinkan Gradle Sync; instal SDK Android 35 / Build Tools 35 bila diminta.
   Koneksi internet diperlukan saat pertama kali mengunduh dependensi.
5. Menu Build -> Build Bundle(s) / APK(s) -> Build APK(s).
   (Pada Android Studio versi baru mungkin bernama Build -> Generate APK(s).)
6. Ambil APK: app\build\outputs\apk\debug\app-debug.apk
7. Salin APK itu ke HP Android, instal, dan jalankan.

ALTERNATIF: BUILD OTOMATIS DI GITHUB ACTIONS
--------------------------------------------
1. Buat repository GitHub baru dengan branch utama main.
2. Upload SEMUA ISI folder TokoPintarNative ke ROOT repository,
   termasuk folder .github/workflows/build-apk.yml.
3. Buka tab Actions -> Build APK Android Resmi -> Run workflow.
   (Push ke main juga memulai build.)
4. Pada job yang sukses, buka bagian Artifacts -> Toko-Pintar-Native-APK.
5. Download ZIP artifact, ekstrak app-debug.apk, lalu instal ke HP.
Tidak perlu menyalin APK dari versi lama.

PERANGKAT & FITUR
----------------
- Android 8.0/API 26 dan lebih baru.
- Pertama kali buka: buat password akun admin (minimal 6 karakter).
- Admin: produk, harga, stok, laporan, karyawan, printer, dan backup.
- Karyawan: kasir dan stok melalui kamera.
- Kamera: ambil foto referensi produk di halaman Edit Produk.
  Kamera membantu mengurutkan produk yang mirip pada katalog melalui
  perceptual image hash; pemilihan barang tetap wajib dikonfirmasi.
- Stok lewat kamera: foto -> pilih barang -> ketuk barang di foto atau isi
  jumlah manual -> pilih MASUK / KELUAR / OPNAME -> Simpan.
- Transaksi: cek stok secara transaksional, kurangi stok, catat nama kasir,
  simpan riwayat, cetak struk.
- Printer Bluetooth: ESC/POS Bluetooth Classic/SPP yang SUDAH di-pairing.
  Untuk Android 12+, izinkan Nearby devices / Bluetooth bila diminta.
- Printer Wi-Fi/LAN: ESC/POS RAW TCP sesuai IP printer, biasanya port 9100,
  HP dan printer berada dalam jaringan lokal yang saling terhubung.
  Perintah cetak RAW TCP tidak terenkripsi; gunakan Wi-Fi toko tepercaya.
- Kertas struk: 58mm (32 karakter) atau 80mm (48 karakter).
- Penyimpanan: database SQLite lokal, tidak ada akun cloud.
- Backup: JSON; SIMPAN FOTO REFERENSI TERPISAH, karena berkas foto tidak
  disertakan ke backup JSON versi awal.

BATASAN YANG PERLU DIKETAHUI
---------------------------
- Ini bukan AI pengenal barang curah secara universal. Hasil kemiripan foto
  dapat salah; jumlah barang bukan dihitung otomatis oleh AI.
- Printer BLE dan protokol printer non-ESC/POS tidak otomatis didukung.
- Cetak ke printer di internet/jarak jauh di luar LAN belum tersedia.
- Akun karyawan dan stok tidak tersinkron antar-HP. Semua lokal satu HP.
- Data APK lama tidak berpindah otomatis karena package ID baru dan skema baru.
- Proyek telah lolos pemeriksaan sintaks/tipenya dengan stub API Android
  dan tes formatter struk Java, TETAPI belum berhasil dikompilasi dengan
  Android SDK resmi dan belum dites pada HP fisik di lingkungan penyusun.
- Jika Android Studio build gagal, kirim file output Build (pesan error
  lengkap), bukan hanya screenshot layar kosong.

PENGEMBANGAN
------------
Build: Android Gradle Plugin 8.7.3, Gradle 8.9, JDK 17, compileSdk 35.
Tanpa AndroidX dependency tambahan dan tanpa library pihak ketiga.
Folder .github/workflows menyediakan workflow build resmi.

Pengembangan ini adalah implementasi mandiri, bukan salinan kode proprietari.

CARA ALTERNATIF PALING MUDAH (WINDOWS + ANDROID STUDIO SUDAH TERPASANG)
-----------------------------------------------------------------------
1. Pastikan Android Studio SDK Manager sudah menginstal Android API 35.
2. Klik dua kali BUILD-APK-WINDOWS.bat.
3. Script mengunduh Gradle 8.9 dari services.gradle.org jika diperlukan,
   lalu menggunakan Android SDK asli untuk mengompilasi APK.
4. Hasil ada di app\build\outputs\apk\debug\app-debug.apk.
Script tidak merekayasa DEX; build harus menyelesaikan tugas assembleDebug.
