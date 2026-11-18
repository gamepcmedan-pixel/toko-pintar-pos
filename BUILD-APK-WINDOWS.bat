@echo off
cd /d "%~dp0"
echo Build APK Toko Pintar POS Native melalui Android SDK dan Gradle resmi.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0BUILD-APK-WINDOWS.ps1"
if errorlevel 1 (
  echo.
  echo Build gagal. Simpan pesan error di atas dan kirim untuk diperbaiki.
  pause
  exit /b 1
)
echo Selesai. APK ada di app\build\outputs\apk\debug\app-debug.apk
pause
