# From scratch vs reused

| Piece | Status | Detail |
|---|---|---|
| `launcher/olekalauncher/` | **From scratch** | Own .desktop parser, fuzzy matcher, GTK3 + layer-shell window, recents ranking. Uses GTK and gtk-layer-shell as libraries only. |
| `scripts/gen-theme.py`, `theme/palette.toml` | **From scratch** | Palette renderer for sway, waybar, foot and the launcher. |
| `oleka-status`, `oleka-welcome`, `oleka-boot-check` | **From scratch** | Small shell scripts. |
| `scripts/build.sh`, `qemu-test.sh`, `stage.sh`, CI workflow | **From scratch** | Glue around live-build and QEMU. |
| waybar | **Customised** | Stock Debian package. Our config, CSS layout, palette and one custom module. No source changes. |
| sway, swaybg, swaylock, swayidle | **Reused, configured** | Stock Debian packages with our config. |
| foot | **Reused, themed** | Stock package, generated colours and font. |
| live-build, live-boot, live-config | **Reused** | Debian tooling that makes the ISO. |
| Debian packages (kernel, firefox-esr, pipewire, NetworkManager, fonts) | **Reused** | Unmodified. |
