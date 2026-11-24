# oleka-launcher

A small application launcher for Wayland, written from scratch in Python 3 and GTK 3.
Press a key, type a few letters, press Enter.

## What it does
- Shows a centered overlay (layer-shell, so it sits above windows and takes keyboard focus).
- Reads `.desktop` files from `~/.local/share/applications` and `/usr/share/applications`
  (also `XDG_DATA_HOME` / `XDG_DATA_DIRS`). Skips `NoDisplay` and `Hidden` entries.
  A file in `~/.local` overrides a system file with the same name.
- Fuzzy search on name and comment: prefix, word prefix, substring, then in-order letters ("ffx" finds Firefox).
- Up/Down move, Enter launches, Esc (or clicking away) closes.
- Remembers launch counts in `~/.cache/oleka-launcher/recents.json`. Used apps get a small ranking boost
  and come first when the search box is empty.
- Exec field codes (`%U`, `%f` ...) are removed, `%%` becomes `%`.

## Install (Debian trixie)
    sudo apt install python3 python3-gi gir1.2-gtk-3.0 gir1.2-gtklayershell-0.1
    sudo make install          # /usr/local/bin/oleka-launcher + /usr/local/share/oleka-launcher/style.css
Bind `oleka-launcher` to a key. niri example: `Mod+Space { spawn "oleka-launcher"; }`.

Run from source: `make run`. Tests (no GTK needed): `sudo apt install python3-pytest`, then `make test`.
If gtk-layer-shell is missing it still works as a normal borderless window.

## Theme
`style.css` holds the palette in five `@define-color` lines (bg #1e1e2e, surface #313244, text #cdd6f4,
accent #89b4fa, muted #6c7086), radius 10px, font Inter then Noto Sans.
Copy it to `~/.config/oleka-launcher/style.css` to override.

## Layout
- `olekalauncher/apps.py`    parse .desktop files, build the command
- `olekalauncher/search.py`  scoring and ranking
- `olekalauncher/recents.py` launch counts
- `olekalauncher/ui.py`      the GTK window
- `tests/`                   parsing, matching, recents

## Originality
Written for this project. It uses the freedesktop Desktop Entry format and the GTK and gtk-layer-shell APIs.

## Tested
Unit tests (6, pass). GUI run under Xvfb with typing, arrows and Enter, launch recorded.
Not tested: real Wayland layer-shell (centering, focus) on a Debian live image.
