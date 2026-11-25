#!/bin/sh
# Boot the ISO with a virtual GPU and save screenshots of the desktop via the QEMU monitor.
# Software emulation is slow, so we take one every 60 s for up to ~14 minutes.
set -u
ISO="${1:-oleka-desktop.iso}"; OUT="${2:-shots}"
mkdir -p "$OUT"
ACCEL="-accel tcg"; [ -w /dev/kvm ] && ACCEL="-accel kvm"
rm -rf kx && mkdir kx
xorriso -osirrox on -indev "$ISO" -extract /live kx 2>&1 | tail -1
KER=$(ls kx/vmlinuz* | head -1); INI=$(ls kx/initrd* | head -1)
rm -f /tmp/mon.sock
qemu-system-x86_64 -m 3072 -smp 4 $ACCEL -cdrom "$ISO" -boot d -kernel "$KER" -initrd "$INI" \
  -append "boot=live components username=oleka hostname=oleka-desktop console=tty0 console=ttyS0,115200" \
  -vga virtio -display none -serial file:"$OUT/serial.log" \
  -monitor unix:/tmp/mon.sock,server,nowait -daemonize -pidfile /tmp/qemu.pid
n=0
while [ $n -lt 14 ]; do
  sleep 60; n=$((n+1))
  echo "shot $n, serial $(wc -c < "$OUT/serial.log") bytes"
  printf 'screendump /tmp/s.ppm\n' | nc -U -N /tmp/mon.sock >/dev/null 2>&1 || printf 'screendump /tmp/s.ppm\n' | nc -U -w1 /tmp/mon.sock >/dev/null 2>&1
  sleep 1
  [ -s /tmp/s.ppm ] && convert /tmp/s.ppm "$OUT/shot-$(printf %02d $n).png" && cp "$OUT/shot-$(printf %02d $n).png" "$OUT/latest.png"
done
kill "$(cat /tmp/qemu.pid)" 2>/dev/null; ls -l "$OUT"
