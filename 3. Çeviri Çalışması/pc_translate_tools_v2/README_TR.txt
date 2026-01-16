KULLANIM

1) Orijinal ucs.pc dosyasini bu klasore koy.
2) 01_unpack.bat uzerine ucs.pc'yi surukle-birak -> ucs_translate.tsv cikar.
3) ucs_translate_TR.tsv dosyasini hazirla (ID<TAB>TR_METIN).
4) 02_build.bat uzerine ucs_translate_TR.tsv'yi surukle-birak -> ucs_tr.pc uretilir.

NOT
- Script iki farkli .pc header formatini otomatik tanir (zlib'in 4. veya 8. baytta baslamasi).
- Yer tutuculari (%1, \n vb.) ceviride bozmamaya dikkat et.
