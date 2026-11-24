#!/bin/sh
# Copy the from-scratch launcher into the image tree before building (same layout as launcher/Makefile).
set -e
cd "$(dirname "$0")/.."
python3 scripts/gen-theme.py
make -C launcher install DESTDIR="$PWD/config/includes.chroot" PREFIX=/usr/local
