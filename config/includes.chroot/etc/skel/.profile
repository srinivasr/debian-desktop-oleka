# Start the Wayland session on tty1 after autologin.
if [ -z "$WAYLAND_DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    export XDG_SESSION_TYPE=wayland XDG_CURRENT_DESKTOP=sway
    exec sway
fi
