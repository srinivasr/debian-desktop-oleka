"""The window. GTK 3 via PyGObject.

On Wayland it asks for a layer-shell surface (above windows, takes keyboard focus)
if gtk-layer-shell is installed. Otherwise it is a plain borderless window, which
is also what runs under Xvfb in tests.
"""
import os
import subprocess

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell
except (ValueError, ImportError):
    GtkLayerShell = None

from . import apps as appslib  # noqa: E402
from . import recents
from .search import rank  # noqa: E402

# style.css lives next to the package (installed to /usr/local/share/oleka-launcher).
_HERE = os.path.dirname(os.path.abspath(__file__))
CSS_CANDIDATES = [
    os.path.expanduser("~/.config/oleka-launcher/style.css"),   # user override
    "/usr/local/share/oleka-launcher/style.css",                # make install
    os.path.join(_HERE, "..", "style.css"),                     # running from source
]
MAX_RESULTS = 8


def launch(app):
    """Start the app detached from us, so it survives the launcher exiting."""
    args = appslib.command_for(app)
    if not args:
        return False
    try:
        subprocess.Popen(args, start_new_session=True,
                         stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


class Launcher(Gtk.Window):
    def __init__(self, apps):
        super().__init__(title="olekalauncher")
        self.apps = apps
        self.results = []
        self.counts = recents.load()

        self.set_default_size(560, -1)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)  # layer-shell ignores this, centers itself
        self.get_style_context().add_class("olekalauncher")
        self._setup_layer_shell()

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Search applications...")
        self.entry.connect("changed", self.on_changed)
        self.entry.connect("activate", self.on_activate)
        box.pack_start(self.entry, False, False, 0)

        self.list = Gtk.ListBox()
        self.list.connect("row-activated", self.on_row_activated)
        self.list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        box.pack_start(self.list, False, False, 0)

        self.connect("key-press-event", self.on_key)
        self.connect("focus-out-event", lambda *a: Gtk.main_quit()
                     if not os.environ.get("OLEKA_LAUNCHER_KEEP_OPEN") else None)
        self.refresh()

    def _setup_layer_shell(self):
        if GtkLayerShell is None or not GtkLayerShell.is_supported():
            return
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        # No anchors set: the compositor centers the surface on screen.


    def refresh(self):
        for row in self.list.get_children():
            self.list.remove(row)
        self.results = rank(self.entry.get_text(), self.apps, MAX_RESULTS, self.counts)
        for app in self.results:
            self.list.add(self._make_row(app))
        self.list.show_all()
        if self.results:
            self.list.select_row(self.list.get_row_at_index(0))

    def _make_row(self, app):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(spacing=12)
        hbox.get_style_context().add_class("result")
        # Only draw an icon the theme really has; a missing icon would show
        # a broken-image placeholder (or crash on a minimal system).
        theme = Gtk.IconTheme.get_default()
        name_ = app.icon if theme.has_icon(app.icon) else "application-x-executable"
        icon = Gtk.Image()
        if theme.has_icon(name_):
            icon.set_from_icon_name(name_, Gtk.IconSize.LARGE_TOOLBAR)
        icon.set_size_request(24, 24)
        hbox.pack_start(icon, False, False, 0)
        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        name = Gtk.Label(label=app.name, xalign=0)
        name.get_style_context().add_class("name")
        text.pack_start(name, False, False, 0)
        if app.comment:
            sub = Gtk.Label(label=app.comment, xalign=0, ellipsize=3)
            sub.get_style_context().add_class("comment")
            text.pack_start(sub, False, False, 0)
        hbox.pack_start(text, True, True, 0)
        row.add(hbox)
        return row


    def on_changed(self, _entry):
        self.refresh()

    def on_activate(self, _entry):
        row = self.list.get_selected_row()
        if row is not None:
            self.run_index(row.get_index())

    def on_row_activated(self, _list, row):
        self.run_index(row.get_index())

    def run_index(self, index):
        app = self.results[index]
        if launch(app):
            recents.record(app)
            Gtk.main_quit()

    def on_key(self, _widget, event):
        key = event.keyval
        if key == Gdk.KEY_Escape:
            Gtk.main_quit()
            return True
        if key in (Gdk.KEY_Down, Gdk.KEY_Up):
            self.move_selection(1 if key == Gdk.KEY_Down else -1)
            return True
        return False

    def move_selection(self, step):
        if not self.results:
            return
        row = self.list.get_selected_row()
        index = (row.get_index() if row else 0) + step
        index = max(0, min(len(self.results) - 1, index))
        self.list.select_row(self.list.get_row_at_index(index))


def load_css():
    provider = Gtk.CssProvider()
    path = next((p for p in CSS_CANDIDATES if os.path.exists(p)), None)
    if path is None:
        return
    provider.load_from_path(path)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)


def main():
    load_css()
    win = Launcher(appslib.load_apps())
    win.show_all()
    win.entry.grab_focus()
    Gtk.main()
