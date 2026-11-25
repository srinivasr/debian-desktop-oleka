# Oleka Desktop

A small Debian-based live ISO with a Wayland desktop. Built for the Oleka Labs take-home
"Build a Custom Debian Desktop Distribution".

- Base: Debian 13 (trixie), built with `live-build`
- Compositor: sway (Wayland, wlroots)
- Panel: waybar, customised (own module, own layout, shared theme)
- Launcher: `oleka-launcher`, written from scratch in this repo (`launcher/`)
- Theme: one palette file, `theme/palette.toml`, rendered into every component

Demo: [demo.mp4](https://github.com/s0mth1n/debian-desktop-oleka/releases/download/v1.0/demo.mp4), a sped-up recording (about 2 min, no audio) of the real ISO in QEMU on CI.

## Build and test

CircleCI builds the ISO and boot-tests it on every push (`.circleci/config.yml`). The GitHub Actions workflow
(`.github/workflows/build.yml`) does the same, but Actions is disabled on the account that holds this repo, so it has not run.
Without CI, `sh scripts/build-docker.sh` does the same on any machine with Docker and QEMU. By hand on Debian 13:

    sudo apt install live-build qemu-system-x86 xorriso git make python3
    sudo sh scripts/build.sh                    # makes oleka-desktop.iso and oleka-desktop.sha256
    sh scripts/qemu-test.sh oleka-desktop.iso   # headless boot, waits for the serial marker
    qemu-system-x86_64 -m 2048 -enable-kvm -cdrom oleka-desktop.iso -boot d   # to look at it

Login is automatic (user `oleka`, no password on the live image).

## Reproducibility

The package set is pinned to a snapshot.debian.org timestamp (`SNAPSHOT`, default
`20251101T000000Z`) and `SOURCE_DATE_EPOCH` is set to the last commit time, so the same commit gives the same
packages. The ISO itself is not bit-identical: two builds of commit bf77b72 on CircleCI produced different
SHA-256 hashes. The `repro-check` CI job rebuilds and compares, and stores the result as an artifact. I have not yet
found which part of the image differs.

## Keys

Super+Enter terminal, Super+D launcher, Super+Shift+Q close window, Super+1..4 workspaces,
Super+Shift+S screenshot, Super+Shift+E exit.

## Docs

- `docs/ARCHITECTURE.md` design and decisions
- `docs/REUSE.md` what is from scratch and what is reused or customised
- `docs/WALKTHROUGH.md` notes for explaining the project and the demo script

## Status

See "Known gaps" in `docs/ARCHITECTURE.md`.
