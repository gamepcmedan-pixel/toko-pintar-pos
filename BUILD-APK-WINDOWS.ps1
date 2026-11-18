# Compiles Android APK using official Gradle + installed Android SDK.
# Does not patch or manufacture a DEX file.
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host '[1/4] Memeriksa JDK 17 dan Android SDK...' -ForegroundColor Cyan
$studioJbr = Join-Path $env:ProgramFiles 'Android\Android Studio\jbr'
if (Test-Path (Join-Path $studioJbr 'bin\java.exe')) {
  $env:JAVA_HOME = $studioJbr
  $env:PATH = (Join-Path $studioJbr 'bin') + ';' + $env:PATH
}
try { & java --version | Out-Host } catch { throw 'Java tidak ditemukan. Instal Android Studio (termasuk JBR 17+).' }
if ($LASTEXITCODE -ne 0) { throw 'Perlu Java 17 atau lebih baru. Aktifkan JBR dari Android Studio.' }

$candidates = @($env:ANDROID_HOME, $env:ANDROID_SDK_ROOT, (Join-Path $env:LOCALAPPDATA 'Android\Sdk'))
$sdk = $null
foreach ($item in $candidates) {
  if ($item -and (Test-Path (Join-Path $item 'platforms\android-35\android.jar'))) {
    $sdk = $item
    break
  }
}
if (-not $sdk) {
  throw 'Android SDK Platform 35 tidak ditemukan. Buka Android Studio > Tools > SDK Manager > install Android 15 (API 35), kemudian jalankan script ini lagi.'
}
$env:ANDROID_HOME = $sdk
$env:ANDROID_SDK_ROOT = $sdk
Write-Host "SDK: $sdk"

Write-Host '[2/4] Menyiapkan Gradle 8.9...' -ForegroundColor Cyan
$tools = Join-Path $Root '.build-tools'
$gradle = Join-Path $tools 'gradle-8.9\bin\gradle.bat'
if (-not (Test-Path $gradle)) {
  New-Item -ItemType Directory -Path $tools -Force | Out-Null
  $zip = Join-Path $tools 'gradle-8.9-bin.zip'
  if (-not (Test-Path $zip)) {
    Invoke-WebRequest -Uri 'https://services.gradle.org/distributions/gradle-8.9-bin.zip' -OutFile $zip
  }
  Expand-Archive -Path $zip -DestinationPath $tools -Force
}

Write-Host '[3/4] Build APK dengan Gradle resmi...' -ForegroundColor Cyan
& $gradle '--no-daemon' ':app:assembleDebug'
if ($LASTEXITCODE -ne 0) { throw "Build gagal, kode $LASTEXITCODE. Lihat error Gradle di atas." }

Write-Host '[4/4] Selesai!' -ForegroundColor Green
$apk = Join-Path $Root 'app\build\outputs\apk\debug\app-debug.apk'
if (-not (Test-Path $apk)) { throw "Build tidak menghasilkan APK di $apk" }
Write-Host "APK: $apk" -ForegroundColor Green
Invoke-Item (Split-Path -Parent $apk)
