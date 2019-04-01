from pathlib import Path

import lark
from gettext import gettext
from gi.repository import Gtk
from typing import Optional, Union, List

_ = gettext


class ParsingResultsView:
    ESCAPE_CHARS = {"\a": "\\a", "\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t", "\v": "\\v"}

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(str(Path(__file__).parents[0] / "data" / "ui" / "parsing-results.ui"))
        self.view: Gtk.Stack = builder.get_object("parsing_results")
        self.tree: Gtk.TreeView = builder.get_object("tree")
        self.error_name: Gtk.Label = builder.get_object("error_name")
        self.error_message: Gtk.Label = builder.get_object("error_message")
        self.error_type: Gtk.Label = builder.get_object("error_type")
        builder.get_object("error_message_scroll").add(self.error_message)
        column, _1, _2 = self._create_column("Node type and value", [0, 1])
        column.set_expand(True)
        self.tree.append_column(column)
        position_column, _1, = self._create_column("l:c", [6])
        self.tree.append_column(position_column)

        self.expanded = set()
        self.tree.connect("row-collapsed", self._on_row_collapse)
        self.tree.connect("row-expanded", self._on_row_expand)

    @staticmethod
    def _create_column(title: str, indices: List[int]):
        column = Gtk.TreeViewColumn()
        column.set_title(title)
        yield column
        for i, index in enumerate(indices):
            renderer = Gtk.CellRendererText()
            column.pack_start(renderer, i == len(indices) - 1)
            column.add_attribute(renderer, "text", index)
            yield renderer

    # noinspection PyUnusedLocal
    def _on_row_expand(self, view, iterator, path):
        indices = path.get_indices()
        self.expanded.add(tuple(indices))

    # noinspection PyUnusedLocal
    def _on_row_collapse(self, view, iterator, path):
        indices = path.get_indices()
        self.expanded.remove(tuple(indices))

    def build_from_tree(self, tree: lark.Tree):
        store = Gtk.TreeStore(str, str, int, int, int, int, str)
        self._create_tree_node(store, None, tree)
        self.tree.set_model(store)
        for indices in self.expanded:
            path = Gtk.TreePath.new_from_indices(indices)
            self.tree.expand_to_path(path)
        self.view.set_visible_child_name("tree")

    def _create_tree_node(self, store: Gtk.TreeStore, it: Optional[Gtk.TreeIter], node: Union[lark.Tree, lark.Token]):
        if isinstance(node, lark.Tree):
            children = store.append(it, [node.data, "", -1, -1, -1, -1, ""])
            for child in node.children:
                self._create_tree_node(store, children, child)
        else:
            content = str(node)
            for char, esc in ParsingResultsView.ESCAPE_CHARS.items():
                content = content.replace(char, esc)
            store.append(it, [node.type, content, node.line, node.column, node.end_line, node.end_column,
                              "{}:{}".format(node.line, node.column)])

    def show_error(self, error: Exception):
        self.view.set_visible_child_name("error_box")

        if isinstance(error, lark.GrammarError):
            error_name = _("There is an error in the grammar")
        else:
            error_name = _("The supplied text is invalid")
        self.error_name.set_text(error_name)
        self.error_message.set_text(str(error))

        if hasattr(error, "__module__"):
            module = error.__module__
            if module == "lark.exceptions":
                module = "lark"
            self.error_type.set_text("{}.{}".format(module, error.__class__.__name__))
        else:
            self.error_type.set_text(error.__class__.__name__)
