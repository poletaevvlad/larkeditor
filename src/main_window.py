from pathlib import Path
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gio
from typing import Optional, Set, Dict, Callable
from gettext import gettext
import lark
import re

from buffer_watcher import BufferWatcher
from editor.text_editor import TextEditor
from header_bar import HeaderBar
from lark_parser import LarkParser
from results import ParsingResultsView
from utils import create_file_filter, show_error_message, HotKeys
from editor.source_editor import LarkSourceEditor

_ = gettext
hot_keys = HotKeys()


class MainWindow(Gtk.ApplicationWindow):
    BUFFER_LARK_SOURCE = "lark_source"
    BUFFER_TEXT = "text"

    def __init__(self, application, file: Optional[Path] = None):
        super().__init__(application=application)
        self.set_size_request(800, 600)

        self.parser = LarkParser()
        self.lark_source = LarkSourceEditor()
        if file is not None:
            self.lark_source.load_file(file)
        self.parsing_results = ParsingResultsView()
        self.text_view = TextEditor("white")
        self._create_layout(self.lark_source, self.parsing_results, self.text_view)

        self.watcher = BufferWatcher(1, self._watcher_callback)
        self.watcher.add_buffer(MainWindow.BUFFER_LARK_SOURCE, self.lark_source.buffer)
        self.watcher.add_buffer(MainWindow.BUFFER_TEXT, self.text_view.buffer)
        self.watcher.start()
        self.connect("destroy", lambda window: self.watcher.stop())

        self.header_bar = HeaderBar()
        self.header_bar.apply_to_window(self)
        self.header_bar.init_title(self.lark_source.file_name, self.lark_source.changed)
        self.header_bar.parse_callback = self.watcher.force_processing
        self.parser.running.bind(self.header_bar.set_running)
        hot_keys.apply_to_window(self)

        self._create_action("save", lambda: self._save_file(False))
        self._create_action("save_as", lambda: self._save_file(True))
        self._create_action("load_text", self._open_text)
        self._create_action("save_text", self._save_text)
        self._create_action("run_parsing", self.watcher.force_processing)
        self._create_action("open", self._open_file)

    def _create_action(self, name: str, callback: Callable[[], None]):
        action: Gio.SimpleAction = Gio.SimpleAction.new(name, None)
        action.connect("activate", lambda action, parameter: callback())
        self.add_action(action)

    def _create_layout(self, source_view: LarkSourceEditor, result_view: ParsingResultsView, text_view: TextEditor):
        def _wrap_scroll_view(view):
            scroll_view = Gtk.ScrolledWindow()
            scroll_view.add(view)
            scroll_view.show()
            return scroll_view

        text_view.view.show()
        result_view.view.hide()
        source_view.view.show()

        sidebar_split = Gtk.Paned()
        sidebar_split.set_orientation(Gtk.Orientation.VERTICAL)
        sidebar_split.add1(_wrap_scroll_view(text_view.view))
        sidebar_split.add2(result_view.view)
        sidebar_split.set_position(150)
        sidebar_split.show()

        main_split = Gtk.Paned()
        source_scroll_view = _wrap_scroll_view(source_view.view)
        main_split.add1(source_scroll_view)
        main_split.add2(sidebar_split)
        main_split.show()
        main_split.set_position(400)
        main_split.child_set_property(source_scroll_view, "resize", True)
        main_split.child_set_property(sidebar_split, "resize", False)
        self.add(main_split)

    def _watcher_callback(self, changed: Set[str], texts: Dict[str, str]):
        try:
            grammar = None
            if self.parser.lark is None or MainWindow.BUFFER_LARK_SOURCE in changed:
                grammar = texts[MainWindow.BUFFER_LARK_SOURCE]
            tree = self.parser.parse(texts[MainWindow.BUFFER_TEXT], grammar=grammar)
            GLib.idle_add(self._display_tree, tree)
        except Exception as e:
            GLib.idle_add(self._display_error, e)

    def _display_tree(self, tree: lark.Tree):
        self.lark_source.clear_error()
        self.text_view.clear_error()
        self.parsing_results.build_from_tree(tree)
        self.parsing_results.view.show()

    def _display_error(self, exception: Exception):
        if isinstance(exception, lark.UnexpectedToken):
            self.text_view.underline_error(exception.line - 1, exception.column - 1, len(exception.token))
            self.lark_source.clear_error()
        elif isinstance(exception, lark.UnexpectedCharacters):
            self.text_view.underline_error(exception.line - 1, exception.column - 1, 1)
            self.lark_source.clear_error()
        elif isinstance(exception, lark.GrammarError):
            error_message, = exception.args
            search_result = re.search(r"line\s+(\d+),?\s+col(umn)?\s+(\d+)", error_message)
            if search_result is not None:
                line = int(search_result.group(1)) - 1
                column = int(search_result.group(3)) - 1
                self.text_view.clear_error()
                self.lark_source.underline_error(line, column, 1)
        self.parsing_results.show_error(exception)
        self.parsing_results.view.show()

    @hot_keys.add(Gdk.KEY_O, Gdk.ModifierType.CONTROL_MASK)
    def _open_file(self):
        dialog = Gtk.FileChooserDialog(_("Open grammar"), self, Gtk.FileChooserAction.OPEN,
                                       (_("Cancel"), Gtk.ResponseType.CANCEL, _("OK"), Gtk.ResponseType.ACCEPT))
        dialog.add_filter(create_file_filter(_("Lark grammar"), patterns=["*.lark"]))
        dialog.add_filter(create_file_filter(_("All files"), patterns=["*"]))
        result = dialog.run()
        if result == Gtk.ResponseType.ACCEPT:
            filename = Path(dialog.get_filename())
            if not self.lark_source.changed.value and self.lark_source.file_name.value is None:
                try:
                    self.lark_source.load_file(filename)
                except OSError as e:
                    show_error_message(self, _("Unable to open a file"),
                                       _("An error has occurred when trying to open a file \"{0}\": {1}")
                                       .format(e.filename, e.strerror))
            else:
                app: Gtk.Application = self.get_application()
                app.activate_action("open", GLib.Variant.new_string(str(filename)))
        dialog.destroy()

    @hot_keys.add(Gdk.KEY_S, Gdk.ModifierType.CONTROL_MASK, [False])
    @hot_keys.add(Gdk.KEY_S, Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK, [True])
    def _save_file(self, new_file: bool):
        file_path = self.lark_source.file_name.value
        if file_path is None or new_file:
            dialog = Gtk.FileChooserDialog(_("Save grammar"), self, Gtk.FileChooserAction.SAVE,
                                           (_("Cancel"), Gtk.ResponseType.CANCEL, _("OK"), Gtk.ResponseType.ACCEPT))
            dialog.add_filter(create_file_filter(_("Lark grammar"), patterns=["*.lark"]))
            dialog.add_filter(create_file_filter(_("All files"), patterns=["*"]))
            if dialog.run() == Gtk.ResponseType.ACCEPT:
                file_path = Path(dialog.get_filename())
            else:
                file_path = None
            dialog.destroy()
        if file_path is None:
            return
        try:
            self.lark_source.save_file(file_path)
        except OSError as e:
            show_error_message(self, _("Unable to save a file"),
                               _("An error has occurred when trying to save a file \"{0}\": {1}")
                               .format(e.filename, e.strerror))

    def _open_text(self):
        dialog = Gtk.FileChooserDialog(_("Open text"), self, Gtk.FileChooserAction.OPEN,
                                       (_("Cancel"), Gtk.ResponseType.CANCEL, _("OK"), Gtk.ResponseType.ACCEPT))
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            try:
                self.text_view.load_file(Path(dialog.get_filename()))
            except IOError as e:
                message = _("Unable to open '{}' for reading:\n{}").format(dialog.get_filename(), str(e))
                show_error_message(self, _("Unable to save a file"), message)
        dialog.destroy()

    def _save_text(self):
        dialog = Gtk.FileChooserDialog(_("Save text as"), self, Gtk.FileChooserAction.SAVE,
                                       (_("Cancel"), Gtk.ResponseType.CANCEL, _("OK"), Gtk.ResponseType.ACCEPT))
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            try:
                self.text_view.save_file(Path(dialog.get_filename()))
            except IOError as e:
                message = _("Unable to open '{}' for writing:\n{}").format(dialog.get_filename(), str(e))
                show_error_message(self, _("Unable to open a file"), message)
        dialog.destroy()
