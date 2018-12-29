from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GtkSource

from .symbols_set import SymbolsSet


def get_context_iter(context: GtkSource.CompletionContext) -> Gtk.TextIter:
    end_iter = context.get_iter()
    if not isinstance(end_iter, Gtk.TextIter):
        end_iter = end_iter[1]
    return end_iter


# noinspection PyMethodMayBeStatic
class CompletionProvider(GObject.GObject, GtkSource.CompletionProvider):
    STATEMENTS = ["%import", "%ignore", "%declare"]

    def __init__(self):
        super().__init__()
        self.symbols_set: SymbolsSet = SymbolsSet()

    def get_proposals(self, iterator):
        text = CompletionProvider.get_prev_chars(iterator, lambda c: c in SymbolsSet.SYMBOL_CHARS or c == "%")
        if not text.startswith("%"):
            for symbol in self.symbols_set.get(text):
                yield GtkSource.CompletionItem.new(symbol, symbol, None, None)
        else:
            for statement in CompletionProvider.STATEMENTS:
                if statement.startswith(text):
                    yield GtkSource.CompletionItem.new(statement[1:], statement, None, None)

    def do_populate(self, context: GtkSource.CompletionContext):
        end_iter = get_context_iter(context)
        self.symbols_set.extract(end_iter)
        proposals = list(self.get_proposals(end_iter))
        if len(proposals) > 0:
            context.add_proposals(self, proposals, True)

    def do_match(self, context: GtkSource.CompletionContext):
        if context.get_activation() == GtkSource.CompletionActivation.USER_REQUESTED:
            return True
        iterator: Gtk.TextIter = get_context_iter(context).copy()
        if not iterator.backward_char():
            return False
        char = iterator.get_char()
        return char in SymbolsSet.SYMBOL_CHARS or char == "%"

    @staticmethod
    def get_prev_chars(iterator, predicate):
        iterator: Gtk.TextIter = iterator.copy()
        t = []
        while iterator.backward_char():
            ch = iterator.get_char()
            if predicate(ch):
                t.append(ch)
            else:
                break
        t.reverse()
        return "".join(t)

    def do_get_start_iter(self, context: GtkSource.CompletionContext, proposal: GtkSource.CompletionProposal):
        if proposal.get_text().startswith("%"):
            iterator = get_context_iter(context).copy()
            iterator.backward_find_char(lambda c, _d: c == "%", None)
            return True, iterator
        else:
            return False
