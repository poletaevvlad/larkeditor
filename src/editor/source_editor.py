from pathlib import Path
from typing import Optional

from gi.repository import GtkSource

from editor.text_editor import TextEditor
from utils import Observable
from .completion import CompletionProvider


class LarkSourceEditor(TextEditor):
    def __init__(self):
        super().__init__("light", "lark")
        self.changed: Observable[bool] = Observable(False)

        completion: GtkSource.Completion = self.view.get_completion()
        completion.add_provider(CompletionProvider())
        completion.set_property("show-headers", False)
        self.buffer.connect("changed", self._on_buffer_changed)

    def _on_buffer_changed(self, _buffer):
        self.changed.set(True)

    def load_file(self, file: Path):
        super().load_file(file)
        self.changed.set(False)

    def save_file(self, file: Optional[Path] = None):
        super().save_file(file)
        self.changed.set(False)
