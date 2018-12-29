from typing import Set
import string
from gi.repository import Gtk


class SymbolsSet:
    SYMBOL_CHARS = {*string.ascii_lowercase, *string.ascii_uppercase, *string.digits, "_", "."}

    def __init__(self):
        self._symbols: Set[str] = set()

    @staticmethod
    def _get_chars(iterator: Gtk.TextIter):
        char = iterator.get_char()
        if char != 0:
            yield char
        while iterator.forward_char():
            yield iterator.get_char()

    def extract(self, iterator: Gtk.TextIter):
        self._symbols.clear()
        symbol = []
        iterator = iterator.get_buffer().get_start_iter()
        is_string = False
        for char in self._get_chars(iterator):
            if char == '"':
                is_string = not is_string
            if not is_string and char in SymbolsSet.SYMBOL_CHARS:
                symbol.append(char)
            elif len(symbol) > 0:
                self._symbols.add("".join(symbol))
                symbol.clear()
        if len(symbol) > 0:
            self._symbols.add("".join(symbol))

    def get(self, substring):
        values = filter(lambda s: substring in s and substring != s, self._symbols)
        return sorted(values, key=lambda s: s.find(substring))
