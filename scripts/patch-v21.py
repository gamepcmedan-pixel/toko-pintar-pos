#!/usr/bin/env python3
"""Apply Android 2.1 fixes to the native v2 source extracted by CI.

The source ZIP remains untouched; verify every expected anchor before modifying it.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JAVA = ROOT / "app/src/main/java/com/tokopintar/nativepos/MainActivity.java"
PRINTER = ROOT / "app/src/main/java/com/tokopintar/nativepos/ThermalPrinter.java"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
GRADLE = ROOT / "app/build.gradle"

def change(path, before, after):
    src = path.read_text(encoding="utf-8")
    if src.count(before) != 1:
        raise ValueError(f"{path}: expected one anchor, got {src.count(before)}: {before[:80]!r}")
    path.write_text(src.replace(before, after), encoding="utf-8")

change(MANIFEST,
       '<uses-permission android:name="android.permission.BLUETOOTH_CONNECT"/>',
       '<uses-permission android:name="android.permission.BLUETOOTH_CONNECT"/>\n    <uses-permission android:name="android.permission.BLUETOOTH_SCAN" android:usesPermissionFlags="neverForLocation"/>')
change(MANIFEST, 'android:label="Toko Pintar POS Baru"', 'android:label="Toko Pintar POS 2.1"')
change(GRADLE, "applicationId 'com.tokopintar.nativepos'", "applicationId 'com.tokopintar.nativepos.v21'")
change(GRADLE, "versionCode 1", "versionCode 2")
change(GRADLE, "versionName '2.0.0'", "versionName '2.1.0'")

change(PRINTER, "BluetoothDevice d=a.getRemoteDevice(mac);a.cancelDiscovery();", """
        BluetoothDevice d=a.getRemoteDevice(mac);
        // Android 12+ requires BLUETOOTH_SCAN to call cancelDiscovery().
        // The discovery cancellation is optional for paired SPP printers.
        if(Build.VERSION.SDK_INT<31 ||
                activity.checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN)==PackageManager.PERMISSION_GRANTED){
            try { a.cancelDiscovery(); } catch(SecurityException ignored) { /* optional */ }
        }""")

change(JAVA, '    private Uri capturedMediaUri;', """
    private Uri capturedMediaUri;
    private byte[] pendingBluetoothPrint;
    private boolean pendingPrinterPicker;
    private TextView pendingPrinterLabel;""")

change(JAVA,
       'Ui.add(body,Ui.secondary(this,"Scan Foto Tanpa Barcode",()->choosePhoto("scan-sale",0)),7);',
       """Ui.add(body,Ui.secondary(this,"Scan Foto Tanpa Barcode",()->choosePhoto("scan-sale",0)),7);
        Ui.add(body,caption("Foto cocok kuat akan otomatis menambah 1 barang ke keranjang. Jika belum pasti, pilih kandidat hasil scan."),7);""")

change(JAVA, '    private void addToCartDialog(StoreDb.Product p){', """
    // One stock-checked path for auto-matches and user-confirmed photo matches.
    private void addScannedItem(long productId){
        StoreDb.Product fresh=db.product(productId);
        if(fresh==null)throw new IllegalArgumentException("Produk tidak ditemukan");
        double existing=cart.containsKey(fresh.id)?cart.get(fresh.id).qty:0;
        if(existing+1 > fresh.stock+0.000001)
            throw new IllegalArgumentException("Stok "+fresh.name+" tidak cukup untuk menambah 1 "+fresh.unit);
        cart.put(fresh.id,new StoreDb.CartLine(fresh,existing+1));
        showPOS();
        notice("Berhasil: "+fresh.name+" (+1 "+fresh.unit+") masuk keranjang");
    }
    private void addToCartDialog(StoreDb.Product p){""")

change(JAVA, """        }else if("scan-sale".equals(photoPurpose)){
            String hash=ImageMatcher.hash(b);List<StoreDb.Product> candidates=ImageMatcher.ranked(db.products(""),hash);
            if(candidates.isEmpty()){new AlertDialog.Builder(this).setMessage("Belum ada foto referensi. Hubungi admin untuk mendaftarkan foto produk.").setPositiveButton("OK",null).show();return;}
            List<StoreDb.Product> shown=candidates.subList(0,Math.min(5,candidates.size()));String[] names=new String[shown.size()];
            for(int i=0;i<shown.size();i++)names[i]=shown.get(i).name+" - "+money(shown.get(i).price);
            new AlertDialog.Builder(this).setTitle("Periksa barang sebelum dijual")
                    .setItems(names,(d,index)->addToCartDialog(shown.get(index))).setNegativeButton("Batal",null).show();
        }""", """        }else if("scan-sale".equals(photoPurpose)){
            String hash=ImageMatcher.hash(b);
            List<StoreDb.Product> candidates=ImageMatcher.ranked(db.products(""),hash);
            if(candidates.isEmpty()){
                new AlertDialog.Builder(this).setTitle("Belum ada foto referensi")
                    .setMessage("Daftarkan foto barang melalui Produk > Edit > Ambil Foto Referensi, lalu scan ulang.")
                    .setPositiveButton("Buka Kasir",(d,w)->showPOS())
                    .setNegativeButton("Tutup",null).show();
                return;
            }
            StoreDb.Product first=candidates.get(0);
            int best=ImageMatcher.distance(first.photoHash,hash);
            int next=candidates.size()>1?ImageMatcher.distance(candidates.get(1).photoHash,hash):64;
            // Never silently sell a low-confidence or ambiguous photo match.
            if(best<=8 && next-best>=5){
                safe(()->addScannedItem(first.id));
                return;
            }
            List<StoreDb.Product> shown=candidates.subList(0,Math.min(5,candidates.size()));
            String[] names=new String[shown.size()];
            for(int i=0;i<shown.size();i++){
                StoreDb.Product p=shown.get(i);
                int dist=ImageMatcher.distance(p.photoHash,hash);
                String quality=dist<=8?"Mirip":dist<=18?"Periksa kembali":"Belum mirip";
                names[i]=p.name+" · "+quality+" · "+money(p.price)+" (+1)";
            }
            new AlertDialog.Builder(this).setTitle("Hasil scan belum pasti")
                .setMessage("Pilih barang yang benar agar otomatis +1 ke keranjang. Batalkan jika tidak ada yang cocok.")
                .setItems(names,(d,index)->safe(()->addScannedItem(shown.get(index).id)))
                .setNegativeButton("Batal",null).show();
        }""")

change(JAVA, """        Ui.add(c,Ui.secondary(this,"Pilih Printer Bluetooth yang sudah Pairing",()->{
            if(Build.VERSION.SDK_INT>=31 && !ThermalPrinter.hasBluetoothPermission(this)){
                requestPermissions(new String[]{Manifest.permission.BLUETOOTH_CONNECT},REQ_BT);return;}
            choosePairedPrinter(selected);
        }),8);""", """        Ui.add(c,Ui.secondary(this,"Pilih Printer Bluetooth yang sudah Pairing",()->{
            if(Build.VERSION.SDK_INT>=31 && !ThermalPrinter.hasBluetoothPermission(this)){
                pendingPrinterPicker=true;pendingPrinterLabel=selected;
                requestPermissions(new String[]{Manifest.permission.BLUETOOTH_CONNECT,Manifest.permission.BLUETOOTH_SCAN},REQ_BT);
                return;
            }
            choosePairedPrinter(selected);
        }),8);""")

change(JAVA, """        if("BT".equals(type) && !ThermalPrinter.hasBluetoothPermission(this)){
            if(Build.VERSION.SDK_INT>=31)requestPermissions(new String[]{Manifest.permission.BLUETOOTH_CONNECT},REQ_BT);
            error("Izinkan Bluetooth, lalu coba cetak lagi");return;
        }""", """        if("BT".equals(type) && !ThermalPrinter.hasBluetoothPermission(this)){
            if(Build.VERSION.SDK_INT>=31){
                pendingBluetoothPrint=payload.clone();
                requestPermissions(new String[]{Manifest.permission.BLUETOOTH_CONNECT,Manifest.permission.BLUETOOTH_SCAN},REQ_BT);
            }else error("Aktifkan izin Bluetooth untuk mencetak");
            return;
        }""")

change(JAVA, """        if(request==REQ_BT){
            if(results.length>0&&results[0]==PackageManager.PERMISSION_GRANTED)notice("Izin Bluetooth diberikan. Pilih printer kembali.");
            else error("Izin Bluetooth ditolak; cetak Bluetooth tidak tersedia");
        }""", """        if(request==REQ_BT){
            byte[] resumePrint=pendingBluetoothPrint;pendingBluetoothPrint=null;
            boolean resumePicker=pendingPrinterPicker;pendingPrinterPicker=false;
            TextView resumeLabel=pendingPrinterLabel;pendingPrinterLabel=null;
            // CONNECT is mandatory; SCAN is optional because cancelDiscovery is guarded.
            if(ThermalPrinter.hasBluetoothPermission(this)){
                if(resumePicker && resumeLabel!=null)choosePairedPrinter(resumeLabel);
                if(resumePrint!=null)printBytes(resumePrint);
            }else{
                new AlertDialog.Builder(this).setTitle("Izin Bluetooth diperlukan")
                    .setMessage("Beri izin Perangkat di Sekitar (Nearby Devices) pada Setelan HP > Aplikasi > Toko Pintar POS 2.1.")
                    .setPositiveButton("OK",null).show();
            }
        }""")

assert "addScannedItem(shown.get(index).id)" in JAVA.read_text()
assert "BLUETOOTH_SCAN" in MANIFEST.read_text()
assert "applicationId 'com.tokopintar.nativepos.v21'" in GRADLE.read_text()
print("PATCH_V21_OK: permissions, auto-cart, side-by-side app ID")
