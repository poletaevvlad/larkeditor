import sys
import signal
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio

from main_window import MainWindow
from typing import List
from pathlib import Path
from gettext import gettext
_ = gettext

from utils import show_error_message


class Application(Gtk.Application):
    APP_ID = "io.guthub.poletaevvlad.lark-debugger"

    def __init__(self):
        super().__init__(application_id=Application.APP_ID, flags=Gio.ApplicationFlags.HANDLES_OPEN)

        new_action = Gio.SimpleAction.new("new", None)
        new_action.connect("activate", self.on_new)
        self.add_action(new_action)

        open_action = Gio.SimpleAction.new("open", GLib.VariantType.new("s"))
        open_action.connect("activate", lambda action, param: self.open(param.get_string()))
        self.add_action(open_action)

    def on_new(self, _action, _parameter):
        window = MainWindow(application=self)
        window.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        window = MainWindow(application=self)
        window.present()

    def open(self, file: str):
        try:
            window = MainWindow(self, file=Path(file))
            window.present()
        except IOError as e:
            message = _("Unable to open '{}' for reading:\n{}").format(file, str(e))
            show_error_message(None, _("Unable to open a file"), message)

    def do_open(self, files: List[Gio.File], _n_files, _hint):
        for file in files:
            self.open(file.get_path())


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = Application()
    app.run(sys.argv)
