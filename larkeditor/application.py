import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio

from typing import List
from pathlib import Path
from gettext import gettext as _

from .main_window import MainWindow
from .utils import show_error_message

VERSION = "0.1.0"


class Application(Gtk.Application):
    APP_ID = "io.github.poletaevvlad.lark-editor"

    def __init__(self):
        super().__init__(application_id=Application.APP_ID, flags=Gio.ApplicationFlags.HANDLES_OPEN)
        GLib.set_application_name(_("Lark Editor"))
        GLib.set_prgname(Application.APP_ID)

        new_action = Gio.SimpleAction.new("new", None)
        new_action.connect("activate", self.on_new)
        self.add_action(new_action)

        open_action = Gio.SimpleAction.new("open", GLib.VariantType.new("s"))
        open_action.connect("activate", lambda action, param: self.open(param.get_string()))
        self.add_action(open_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", lambda action, param: self.open_about())
        self.add_action(about_action)

    def on_new(self, _action, _parameter):
        window = MainWindow(application=self)
        window.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        window = MainWindow(application=self)
        window.present()

    def open(self, file: str) -> bool:
        try:
            window = MainWindow(self, file=Path(file))
            window.present()
            return True
        except IOError as e:
            message = _("Unable to open '{}' for reading:\n{}").format(file, str(e))
            show_error_message(None, _("Unable to open a file"), message)
            return False

    def do_open(self, files: List[Gio.File], _n_files, _hint):
        success = True
        for file in files:
            success = success and self.open(file.get_path())
        if not success:
            exit(1)

    def open_about(self):
        dialog = Gtk.AboutDialog()
        dialog.set_version(VERSION)
        dialog.set_copyright("Copyright © 2019 - Vlad Poletaev")
        dialog.set_license_type(Gtk.License.BSD)
        dialog.show()
