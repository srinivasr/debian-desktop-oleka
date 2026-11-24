#!/bin/sh
# Boot the ISO headless in QEMU and wait for the serial marker. Optional: save a screenshot.
set -e
ISO="${1:-oleka-desktop.iso}"
LOG=qemu-serial.log
: > "$LOG"
qemu-system-x86_64 -m 2048 -smp 2 -cdrom "$ISO" -boot d \
  -display none -serial "file:$LOG" -monitor unix:/tmp/qemu-mon,server,nowait \
  -daemonize -pidfile /tmp/qemu.pid ${KVM:+-enable-kvm}
i=0
while [ $i -lt 90 ]; do
  grep -q OLEKA-BOOT-OK "$LOG" && { echo "PASS: boot marker seen"; kill "$(cat /tmp/qemu.pid)"; exit 0; }
  grep -q OLEKA- "$LOG" && grep -E "OLEKA-(MISSING|SWAY-FAILED)" "$LOG" && { kill "$(cat /tmp/qemu.pid)"; exit 1; }
  sleep 5; i=$((i+1))
done
echo "FAIL: no marker in 450s"; tail -30 "$LOG"; kill "$(cat /tmp/qemu.pid)" || true; exit 1
