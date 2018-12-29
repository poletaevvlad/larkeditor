from pathlib import Path
from typing import Optional, Callable
from gettext import gettext

from utils import Observable, ObservableUnion
from gi.repository import Gtk

_ = gettext


def signal_handle_calls_callback(name: str, *args):
    def handler(self, _object):
        callback = getattr(self, name)
        if callback is not None:
            callback(*args)
    return handler


class HeaderBar:
    def __init__(self):
        ui_path = Path(__file__).parents[1] / "data" / "ui" / "header-bar.ui"
        builder = Gtk.Builder()
        builder.add_from_file(str(ui_path))

        self.header_bar: Gtk.HeaderBar = builder.get_object("header_bar")
        self.popover: Gtk.Popover = builder.get_object("menu_popover")
        builder.connect_signals(self)

        self.open_callback: Callable[[], None] = None
        self.save_callback: Callable[[bool], None] = None

    def apply_to_window(self, window: Gtk.Window) -> None:
        window.set_titlebar(self.header_bar)

    def init_title(self, file_observable: Observable[Optional[Path]], changed_observable: Observable[bool]):
        def _update_header_text(file: Optional[Path], changed: bool):
            if file is None:
                title = _("Unnamed grammar")
                subtitle = None
            else:
                title = file.name
                if title.endswith(".lark"):
                    title = title[:-5]
                subtitle = str(file)

            if changed:
                title = "* " + title
            self.header_bar.set_title(title)
            self.header_bar.set_subtitle(subtitle)

        union = ObservableUnion(file_observable, changed_observable)
        union.bind(_update_header_text)

    def _on_menu_requested(self, button):
        self.popover.set_relative_to(button)
        self.popover.show()
        self.popover.popup()

    _on_save = signal_handle_calls_callback("save_callback", False)
    _on_open = signal_handle_calls_callback("open_callback")
