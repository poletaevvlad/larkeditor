from gettext import gettext
from pathlib import Path
from typing import Optional

from gi.repository import Gtk

from buffer_watcher import BufferWatcher
from utils import Observable, ObservableUnion

_ = gettext


class HeaderBar:
    def __init__(self, watcher: BufferWatcher):
        ui_path = Path(__file__).parents[1] / "data" / "ui"
        builder = Gtk.Builder()
        builder.add_from_file(str(ui_path / "header-bar.ui"))
        builder.connect_signals(self)

        self.watcher = watcher
        self.header_bar: Gtk.HeaderBar = builder.get_object("header_bar")
        self.popover: Gtk.Popover = builder.get_object("menu_popover")
        self.parse_button_stack: Gtk.Stack = builder.get_object("parse-button-stack")

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

    def set_running(self, running: bool):
        if running:
            self.parse_button_stack.set_visible_child_name("parse-button-processing")
        else:
            self.parse_button_stack.set_visible_child_name("parse-button-idle")

    def _on_start_changed(self, editable: Gtk.Entry) -> None:
        text: str = editable.get_text()
        text = text.strip()
        if len(text) > 0:
            self.watcher.set_parameters(start=text)

    def _on_start_blur(self, editable: Gtk.Entry, _data: None) -> None:
        text: str = editable.get_text().strip()
        if (len(text)) == 0:
            editable.set_text("start")
            self.watcher.set_parameters(start="start")

