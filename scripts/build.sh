#!/bin/sh
# Reproducible ISO build. Needs root and live-build (runs in CI or a Debian container).
# Same SNAPSHOT + same repo commit -> same package set. SOURCE_DATE_EPOCH pins timestamps.
set -e
cd "$(dirname "$0")/.."
export SNAPSHOT="${SNAPSHOT:-20251101T000000Z}"
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git log -1 --format=%ct)}"
export LC_ALL=C TZ=UTC
sh scripts/stage.sh
lb clean --purge || true
lb config
lb build
sha256sum live-image-amd64.hybrid.iso | tee oleka-desktop.sha256
mv live-image-amd64.hybrid.iso oleka-desktop.iso
