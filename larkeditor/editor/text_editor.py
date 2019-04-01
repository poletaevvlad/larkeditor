from pathlib import Path
from typing import Optional

from gi.repository import GtkSource
from gi.repository import Gtk
from gi.repository import Pango

from ..utils import Observable


def get_style_scheme_manager() -> GtkSource.StyleSchemeManager:
    manager = GtkSource.StyleSchemeManager.new()
    search_path = manager.get_search_path()
    search_path.insert(0, str(Path(__file__).parents[2] / "data" / "styles"))
    manager.set_search_path(search_path)
    return manager


def get_languages_manager() -> GtkSource.LanguageManager:
    manager = GtkSource.LanguageManager.new()
    search_path = manager.get_search_path()
    search_path.insert(0, str(Path(__file__).parents[2] / "data" / "language-specs"))
    manager.set_search_path(search_path)
    return manager


class TextEditor:
    style_scheme_manager = get_style_scheme_manager()
    language_manager = get_languages_manager()

    def __init__(self, scheme_name: str, language_name: Optional[str] = None):
        if language_name is not None:
            language = TextEditor.language_manager.get_language(language_name)
            self.buffer: GtkSource.Buffer = GtkSource.Buffer.new_with_language(language)
        else:
            self.buffer: GtkSource.Buffer = GtkSource.Buffer.new()

        scheme = TextEditor.style_scheme_manager.get_scheme(scheme_name)
        self.buffer.set_style_scheme(scheme)

        self.view: GtkSource.View = GtkSource.View.new_with_buffer(self.buffer)
        self.view.set_show_line_numbers(True)
        self.view.modify_font(Pango.FontDescription("Monospace 10"))
        self.view.set_pixels_above_lines(1)
        self.view.set_pixels_below_lines(1)
        self.view.set_left_margin(5)
        self.file_name: Observable[Optional[Path]] = Observable(None)

        self.error_tag = self.buffer.create_tag("error_underline", underline=Pango.Underline.ERROR)

    def load_file(self, file: Path):
        with open(str(file)) as f:
            text = f.read()
        self.buffer.begin_not_undoable_action()
        self.buffer.set_text(text)
        self.buffer.end_not_undoable_action()
        self.file_name.set(file)

    def save_file(self, file: Optional[Path] = None):
        if file is None:
            file = self.file_name.value
        assert file is not None
        with open(str(file), "w") as f:
            f.write(self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True))
        self.file_name.set(file)

    def underline_error(self, line_start, column_start, length):
        self.clear_error()
        iter_start: Gtk.TextIter = self.buffer.get_iter_at_line_index(line_start, column_start)
        iter_end: Gtk.TextIter = self.buffer.get_iter_at_offset(iter_start.get_offset() + length)
        self.buffer.apply_tag(self.error_tag, iter_start, iter_end)

    def clear_error(self):
        self.buffer.remove_tag(self.error_tag, self.buffer.get_start_iter(), self.buffer.get_end_iter())
