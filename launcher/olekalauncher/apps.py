"""Find installed applications by reading .desktop files.

Format: the freedesktop.org Desktop Entry spec. We read Name, Exec, Icon, Comment
and the flags that hide an entry.
"""
import os
import re
from dataclasses import dataclass


@dataclass
class App:
    name: str
    exec: str      # command line, still containing %f, %U etc.
    icon: str
    comment: str
    path: str      # the .desktop file it came from


def search_dirs():
    """Directories that may hold .desktop files, user ones first."""
    data_home = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    data_dirs = os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share"
    dirs = [data_home] + data_dirs.split(":")
    return [os.path.join(d, "applications") for d in dirs if d]


def parse_desktop_file(path):
    """Return an App, or None if the file should not be shown."""
    values = {}
    in_main_section = False
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("["):
                    in_main_section = line == "[Desktop Entry]"
                    continue
                if in_main_section and "=" in line:
                    key, _, value = line.partition("=")
                    values[key.strip()] = value.strip()
    except OSError:
        return None

    if values.get("Type", "Application") != "Application":
        return None
    if values.get("NoDisplay") == "true" or values.get("Hidden") == "true":
        return None
    if not values.get("Name") or not values.get("Exec"):
        return None
    return App(
        name=values["Name"],
        exec=values["Exec"],
        icon=values.get("Icon", ""),
        comment=values.get("Comment", ""),
        path=path,
    )


def load_apps(dirs=None):
    """Scan every directory. A file seen earlier wins over a later one with
    the same file name, so ~/.local overrides /usr/share."""
    seen = set()
    apps = []
    for directory in dirs or search_dirs():
        for root, _, files in os.walk(directory):
            for name in sorted(files):
                if not name.endswith(".desktop") or name in seen:
                    continue
                seen.add(name)
                app = parse_desktop_file(os.path.join(root, name))
                if app:
                    apps.append(app)
    apps.sort(key=lambda a: a.name.lower())
    return apps


def command_for(app):
    """Turn the Exec line into an argument list.

    Field codes like %U (file/URL placeholders) are dropped because we start
    the app with no arguments. %% means a literal percent sign.
    """
    cmd = app.exec.replace("%%", "\0")
    cmd = re.sub(r"%[a-zA-Z]", "", cmd).replace("\0", "%")
    return split_command(cmd)


def split_command(text):
    """Split on spaces, keeping "quoted parts" together."""
    args, current, quote = [], "", None
    for ch in text:
        if quote:
            if ch == quote:
                quote = None
            else:
                current += ch
        elif ch in "\"'":
            quote = ch
        elif ch.isspace():
            if current:
                args.append(current)
                current = ""
        else:
            current += ch
    if current:
        args.append(current)
    return args
