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

## The Wayland side

There is no X server. sway is the Wayland compositor. It owns the screen and the input devices, decides where windows
go, and composites what clients draw. Clients connect over a Unix socket in `$XDG_RUNTIME_DIR` and share buffers with
it. sway is built on wlroots, a library that handles display output, input devices, rendering and most protocol
details. We use sway unmodified and only change its config.

Our panel and launcher are ordinary Wayland clients, not part of the compositor. Both use the `wlr-layer-shell`
protocol, which lets a client ask for a surface at a screen edge or above normal windows. waybar takes the top edge and
reserves space so windows do not slide under it. `oleka-launcher` opens as an overlay with exclusive keyboard focus and
exits when you pick an app, press Esc or click away. sway starts waybar itself (`swaybar_command waybar`), and waybar's
workspace module talks to sway over its i3-compatible IPC socket. The launcher needs no IPC: it reads `.desktop` files
and starts the app.

Because both use a standard protocol, they should also run under other wlroots compositors such as niri or labwc.
I have only run them under sway.

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

- Builds are not bit-for-bit reproducible. Two builds of the same commit gave different ISO hashes (see the README).
  The package set is the same, the image bytes are not.
- CI runs on CircleCI because GitHub Actions is blocked on this account by billing. Without KVM the boot test runs
  under software emulation and takes several minutes.
- No installer, live image only. No Secure Boot signing.
- The demo video is a sped-up recording of a real QEMU session on CI, not real time, because CI has no KVM. It was recorded once and the recording script is not kept in this repo.
