#!/usr/bin/env python3
from pathlib import Path
root=Path(__file__).resolve().parent.parent
fmt=root/'app/src/main/java/com/tokopintar/nativepos/ReceiptFormatter.java'
main=root/'app/src/main/java/com/tokopintar/nativepos/MainActivity.java'
gradle=root/'app/build.gradle'
fmt.write_text((root/'scripts/ReceiptFormatterV23.java').read_text(encoding='utf-8'),encoding='utf-8')
s=main.read_text(encoding='utf-8')
replacements=[
 ('String[] paperLabels={"58 mm (32 karakter)","80 mm (48 karakter)"};',
  'String[] paperLabels={"58 mm RPP02N (24 karakter)","58 mm standar (32 karakter)","80 mm (48 karakter)"};'),
 ('paper.setSelection("48".equals(db.setting("paper","32"))?1:0);',
  'String paperSetting=db.setting("paper","24");\n        paper.setSelection("48".equals(paperSetting)?2:("32".equals(paperSetting)?1:0));'),
 ('db.putSetting("paper",paper.getSelectedItemPosition()==1?"48":"32");',
  'db.putSetting("paper",new String[]{"24","32","48"}[paper.getSelectedItemPosition()]);'),
 ('db.setting("paper","32")','db.setting("paper","24")')
]
for before,after in replacements:
  n=s.count(before)
  if n<1: raise RuntimeError(f'Expected anchor missing: {before}')
  s=s.replace(before,after)
main.write_text(s,encoding='utf-8')
g=gradle.read_text(encoding='utf-8')
for before,after in [
 ("applicationId 'com.tokopintar.nativepos.v22'","applicationId 'com.tokopintar.nativepos.v23'"),
 ('versionCode 3','versionCode 4'),
 ("versionName '2.2.0'","versionName '2.3.0'")]:
  if g.count(before)!=1:raise RuntimeError(f'Bad Gradle anchor: {before}')
  g=g.replace(before,after)
gradle.write_text(g,encoding='utf-8')
assert 'out.write(0x0A)' in fmt.read_text()
assert '58 mm RPP02N (24 karakter)' in main.read_text()
print('Receipt fix applied: LF 0x0A, 24-column RPP02N, 32/48 options, no cutter')
