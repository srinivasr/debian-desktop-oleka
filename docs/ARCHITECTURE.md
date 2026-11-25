# Architecture

## How it fits together

`live-build` makes a hybrid ISO from Debian trixie. The package list is `config/package-lists/desktop.list.chroot`,
and everything under `config/includes.chroot/` is copied into the image as is. One hook in `config/hooks/live/` enables
NetworkManager and the boot check and sets up autologin on tty1.

On boot, tty1 logs in the live user `oleka`. `~/.profile` (from `/etc/skel`) then runs `exec sway`. sway reads
`~/.config/sway/config`, which starts waybar as its bar and binds Super+D to our launcher.

Colours, font and corner radius live in one file, `theme/palette.toml`. `scripts/gen-theme.py` writes them into the sway,
waybar, foot and launcher config. `tests/` checks that every rendered file carries the same accent colour and that the
palette has all the keys.

## Decisions

I picked sway over niri because niri is not in Debian 13. Using it would mean building from source or adding an
unofficial repo, which works against a pinned build.

The package set is pinned to a snapshot.debian.org date. That gives a fixed set of packages without running our own mirror.

The launcher is Python with GTK 3 and gtk-layer-shell. All three are Debian packages, there is no build step, and the
code is short enough to read in one sitting.

waybar is customised, not forked. We changed its config and CSS, gave it the shared palette, and added one module,
`oleka-status`, that shows memory use and load. No waybar source was touched.

The boot self-test is a systemd service, `oleka-boot-check`. It checks that the binaries and theme files exist, starts
sway headless, and prints `OLEKA-BOOT-OK` on the serial console. `scripts/qemu-test.sh` boots the kernel and initrd
straight from the ISO with a serial console and waits for that line. A pass means the image boots and sway starts. It
says nothing about how the desktop looks. For that, CI also boots the ISO with a virtual GPU and saves screenshots.

## Known gaps

- Bit-for-bit reproducibility between two builds is not verified.
- The first CI run may need package-list fixes. Status is in the repo's Actions tab.
- No installer (live image only). No Secure Boot signing.
- The 2-minute demo recording is made by the author, not generated.
