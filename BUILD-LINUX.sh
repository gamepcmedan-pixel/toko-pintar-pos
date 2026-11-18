#!/bin/sh
set -eu
cd "$(dirname "$0")"
if ! command -v gradle >/dev/null 2>&1; then
  echo 'Install Gradle 8.9 atau gunakan Android Studio / GitHub Actions.'
  exit 1
fi
gradle --no-daemon :app:assembleDebug
echo 'APK: app/build/outputs/apk/debug/app-debug.apk'
