#!/usr/bin/env python3
# 02_build_pc.py
# Orijinal .pc + cevrilmis TSV -> yeni .pc
#
# Kullanim:
#   py 02_build_pc.py ucs.pc ucs_translate_TR.tsv ucs_tr.pc

import sys, struct, zlib, pathlib, re, binascii

RX = re.compile(r"^(\d+)\t(.*)$")
SPLIT_RX = re.compile(r"(\r\n|\n|\r)")
ZLIB_FLG = {0x01, 0x5E, 0x9C, 0xDA}


def detect_format(data: bytes):
    if len(data) >= 6 and data[4] == 0x78 and data[5] in ZLIB_FLG:
        # Format A: [u32 uncompressed_len] + zlib(to EOF)
        uncompressed_len = struct.unpack("<I", data[:4])[0]
        comp_start = 4
        comp_end = len(data)
        return "A", uncompressed_len, None, comp_start, comp_end

    if len(data) >= 10 and data[8] == 0x78 and data[9] in ZLIB_FLG:
        # Format B: [u32 uncompressed_len][u32 compressed_len] + zlib(compressed_len)
        uncompressed_len, compressed_len = struct.unpack("<II", data[:8])
        comp_start = 8
        comp_end = 8 + compressed_len
        return "B", uncompressed_len, compressed_len, comp_start, comp_end

    head16 = binascii.hexlify(data[:16]).decode()
    raise SystemExit(f".pc formati taninamadi. Ilk 16 bayt: {head16}")


def main():
    if len(sys.argv) < 4:
        print("Kullanim: py 02_build_pc.py <orijinal.pc> <translate_TR.tsv> <cikti.pc>")
        sys.exit(1)

    pc_path = pathlib.Path(sys.argv[1])
    tr_path = pathlib.Path(sys.argv[2])
    out_pc  = pathlib.Path(sys.argv[3])

    # 1) Orijinali ac + format tespit
    data = pc_path.read_bytes()
    fmt, uncompressed_len, compressed_len, comp_start, comp_end = detect_format(data)
    raw = zlib.decompress(data[comp_start:comp_end])

    if len(raw) != uncompressed_len:
        raise SystemExit(f"Orijinal pc decompress uzunlugu uyusmuyor. format={fmt} raw={len(raw)} header={uncompressed_len}")

    # 2) Encoding + BOM
    has_bom = raw.startswith(b"\xff\xfe")
    if has_bom:
        text = raw.decode("utf-16le")
        if text.startswith("\ufeff"):
            bom = "\ufeff"
            text_wo_bom = text[1:]
        else:
            bom = ""
            text_wo_bom = text
        enc = "utf-16le"
    else:
        bom = ""
        text_wo_bom = raw.decode("utf-8")
        enc = "utf-8"

    # 3) TR haritasini oku
    tr_text = tr_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    tr_map = {}
    for line in tr_text.split("\n"):
        if not line.strip():
            continue
        m = RX.match(line)
        if not m:
            raise SystemExit("translate_TR.tsv formati bozuk: Her satir ID<TAB>METIN olmali.")
        tr_map[m.group(1)] = m.group(2)

    # 4) Orijinal metni newline ayiricilariyla birlikte parcala
    parts = SPLIT_RX.split(text_wo_bom)  # [line, sep, line, sep, ...]
    out_parts = []
    replaced = 0

    i = 0
    while i < len(parts):
        line = parts[i]
        sep = parts[i + 1] if i + 1 < len(parts) else ""

        m = RX.match(line)
        if m and m.group(1) in tr_map:
            out_parts.append(m.group(1) + "\t" + tr_map[m.group(1)])
            replaced += 1
        else:
            out_parts.append(line)

        out_parts.append(sep)
        i += 2

    merged = "".join(out_parts)

    # 5) Encode + compress + ayni header formatinda yaz
    merged_bytes = (bom + merged).encode(enc)
    comp = zlib.compress(merged_bytes, level=9)

    if fmt == "A":
        header = struct.pack("<I", len(merged_bytes))
    else:
        header = struct.pack("<II", len(merged_bytes), len(comp))

    out_pc.write_bytes(header + comp)

    print(f"OK: {out_pc.name} uretildi. format={fmt} cevrilen satir: {replaced}")


if __name__ == "__main__":
    main()
