#!/usr/bin/env python3
"""Write the Oleka wallpaper (vertical gradient plus an accent line) as a PNG, stdlib only.
Colours come from the generated sway colors.conf so it follows theme/palette.toml."""
import re, struct, zlib, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
conf = (ROOT / "config/includes.chroot/etc/skel/.config/sway/colors.conf").read_text()
col = {k: tuple(int(v[i:i+2], 16) for i in (1, 3, 5)) for k, v in re.findall(r"set \$(\w+) (#\w{6})", conf)}
W, H = 1920, 1080
top, bot, acc = col["bg"], col["surface"], col["accent"]
rows = []
for y in range(H):
    t = y / (H - 1)
    base = [round(top[i] + (bot[i] - top[i]) * t * 0.8) for i in range(3)]
    row = bytearray()
    for x in range(W):
        near = abs(y - (H - 90)) < 2 and 140 < x < 520
        row += bytes(acc if near else base)
    rows.append(b"\x00" + bytes(row))
raw = zlib.compress(b"".join(rows), 9)
def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)) + chunk(b"IDAT", raw) + chunk(b"IEND", b"")
out = ROOT / "config/includes.chroot/usr/share/backgrounds/oleka.png"
out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(png); print("wrote", out, len(png))
