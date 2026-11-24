# Walkthrough notes (for explaining the project) and demo script

## Explain it in two minutes

1. `live-build` turns a package list plus a folder of files into an ISO (`auto/config`, `config/`).
2. On boot the live user logs in on tty1 and sway starts (`~/.profile`).
3. sway shows waybar on top. Waybar is the stock panel, but we changed config, layout and added a module, `oleka-status`.
4. `Super+D` opens `oleka-launcher`, which we wrote: it reads `.desktop` files, filters as you type, runs the app.
5. One file, `theme/palette.toml`, sets colours for all of it. Change a colour, run `gen-theme.py` and rebuild, and everything follows.
6. CI builds the ISO and boots it in QEMU and waits for a serial marker.

## Likely questions

- Why sway and not niri? niri is not in Debian 13. See ARCHITECTURE.
- What is reproducible? Package set (snapshot pin) and timestamps. Not yet proven bit-identical.
- What did you write? See REUSE.md.

## 2-minute demo script

0:00 Show the repo and the CI run (build and boot test).
0:20 Boot the ISO in QEMU. It reaches the desktop by itself.
0:45 Point at the panel: workspaces, clock, the `mem` module (ours).
1:05 Press Super+D, type "fire", launch Firefox. Press Esc on another open.
1:30 Open `theme/palette.toml` and show the generated colour files that match it (sway, waybar, foot, launcher). Changing a colour needs a rebuild of the ISO, so do not do it live.
1:50 Show REUSE.md and say what is from scratch.
