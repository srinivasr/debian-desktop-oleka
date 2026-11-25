#!/bin/sh
# Boot the ISO headless in QEMU and wait for the serial marker.
# Uses KVM when /dev/kvm is usable, otherwise slow software emulation (TCG).
set -u
ISO="${1:-oleka-desktop.iso}"
LOG=qemu-serial.log
: > "$LOG"
ACCEL="-accel tcg"
if [ -w /dev/kvm ]; then ACCEL="-accel kvm"; fi
echo "qemu accel: $ACCEL, iso: $(ls -l "$ISO")"
qemu-system-x86_64 -m 2048 -smp 4 $ACCEL -cdrom "$ISO" -boot d \
  -display none -serial "file:$LOG" -no-reboot \
  -daemonize -pidfile /tmp/qemu.pid 2>&1
rc=$?
echo "qemu start rc=$rc"
[ "$rc" = 0 ] || exit 1
i=0
while [ $i -lt 180 ]; do
  if grep -q OLEKA-BOOT-OK "$LOG"; then
    echo "PASS: boot marker seen after $((i*5))s"; kill "$(cat /tmp/qemu.pid)"; exit 0
  fi
  if grep -qE "OLEKA-(MISSING|SWAY-FAILED)" "$LOG"; then
    echo "FAIL:"; grep -E "OLEKA-" "$LOG"; kill "$(cat /tmp/qemu.pid)"; exit 1
  fi
  sleep 5; i=$((i+1))
  # heartbeat so CI does not think we hung
  [ $((i % 6)) = 0 ] && echo "waiting $((i*5))s, serial log $(wc -c < "$LOG") bytes, last: $(tail -c 120 "$LOG" | tr -d '\r' | tail -n 1)"
done
echo "FAIL: no marker in 900s. Serial log tail:"; tail -40 "$LOG"
kill "$(cat /tmp/qemu.pid)" 2>/dev/null; exit 1
