import sys
import signal
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk
from gi.repository import Gio

from main_window import MainWindow
from typing import List
from pathlib import Path


class Application(Gtk.Application):
    APP_ID = "io.guthub.poletaevvlad.lark-debugger"

    def __init__(self):
        super().__init__(application_id=Application.APP_ID, flags=Gio.ApplicationFlags.HANDLES_OPEN)

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        window = MainWindow(application=self)
        window.present()

    def do_open(self, files: List[Gio.File], n_files, hint):
        for file in files:
            window = MainWindow(self, file=Path(file.get_path()))
            window.present()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = Application()
    app.run(sys.argv)
