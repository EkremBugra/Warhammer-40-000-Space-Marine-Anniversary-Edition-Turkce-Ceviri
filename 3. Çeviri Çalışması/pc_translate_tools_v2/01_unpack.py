#!/usr/bin/env python3
# 01_unpack.py
# ucs.pc -> ucs_translate.tsv (UTF-8)
#
# Bu script iki olasi .pc formatini otomatik tanir:
#   Format A:
#     [4 byte] uncompressed_len (LE)
#     [zlib]   icerik (dosya sonuna kadar)
#   Format B:
#     [4 byte] uncompressed_len (LE)
#     [4 byte] compressed_len   (LE)
#     [zlib]   icerik (compressed_len kadar)
#
# Cikis: sadece cevrilecek satirlar (ID<TAB>EN_TEXT)

import sys, struct, zlib, pathlib, re, binascii

RX = re.compile(r"^(\d+)\t(.*)$")
ZLIB_FLG = {0x01, 0x5E, 0x9C, 0xDA}

def detect_format(data: bytes):
    if len(data) >= 6 and data[4] == 0x78 and data[5] in ZLIB_FLG:
        # Format A
        uncompressed_len = struct.unpack("<I", data[:4])[0]
        comp_start = 4
        comp_end = len(data)
        return "A", uncompressed_len, comp_start, comp_end

    if len(data) >= 10 and data[8] == 0x78 and data[9] in ZLIB_FLG:
        # Format B
        uncompressed_len, compressed_len = struct.unpack("<II", data[:8])
        comp_start = 8
        comp_end = 8 + compressed_len
        return "B", uncompressed_len, comp_start, comp_end

    head16 = binascii.hexlify(data[:16]).decode()
    raise SystemExit(f".pc formati taninamadi. Ilk 16 bayt: {head16}")


def main():
    if len(sys.argv) < 2:
        print("Kullanim: py 01_unpack.py <dosya.pc>")
        sys.exit(1)

    in_path = pathlib.Path(sys.argv[1])
    data = in_path.read_bytes()

    fmt, uncompressed_len, comp_start, comp_end = detect_format(data)
    raw = zlib.decompress(data[comp_start:comp_end])

    if len(raw) != uncompressed_len:
        raise SystemExit(f"Decompress uzunlugu header ile uyusmuyor. format={fmt} raw={len(raw)} header={uncompressed_len}")

    # decode
    if raw.startswith(b"\xff\xfe"):
        text = raw.decode("utf-16le")
        text = text.lstrip("\ufeff")
    else:
        text = raw.decode("utf-8")

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    out_lines = [line for line in lines if RX.match(line)]

    out_path = in_path.with_name(in_path.stem + "_translate.tsv")
    out_path.write_text("\n".join(out_lines), encoding="utf-8", newline="\n")

    print(f"OK: {out_path.name} olusturuldu. format={fmt} cevrilecek satir: {len(out_lines)}")


if __name__ == "__main__":
    main()
