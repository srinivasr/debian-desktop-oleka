#!/bin/sh
# Build and boot-test the ISO on any machine with Docker (or Podman) and QEMU. No GitHub Actions needed.
# Same container recipe as CI. Needs --privileged because live-build mounts and chroots.
set -e
cd "$(dirname "$0")/.."
RT="${CONTAINER_RT:-docker}"
$RT run --rm --privileged -v "$PWD":/w -w /w debian:trixie bash -c '
  apt-get update && apt-get install -y live-build git python3 make sudo ca-certificates xorriso squashfs-tools &&
  git config --global --add safe.directory /w &&
  sh scripts/build.sh'
echo "ISO: $PWD/oleka-desktop.iso"
if command -v qemu-system-x86_64 >/dev/null; then
  KVM=$([ -w /dev/kvm ] && echo 1) sh scripts/qemu-test.sh oleka-desktop.iso
else
  echo "qemu-system-x86_64 not found, skipping the boot test"
fi
