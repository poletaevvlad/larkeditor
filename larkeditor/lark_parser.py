import lark
from typing import Optional
from .utils import Observable
from gi.repository import GLib


class LarkParser:
    def __init__(self):
        self.lark: Optional[lark.Lark] = None
        self.running: Observable[bool] = Observable(False)

    def parse(self, text: str, grammar: str = None, start: str = None, parser: str = None) -> lark.Tree:
        GLib.idle_add(self.running.set, True)
        try:
            if grammar is not None:
                parser = lark.Lark(grammar, propagate_positions=True, start=start, parser=parser)
                self.lark = parser
            return self.lark.parse(text)
        finally:
            GLib.idle_add(self.running.set, False)
