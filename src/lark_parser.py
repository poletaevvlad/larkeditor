import lark
from typing import Optional


class LarkParser:
    def __init__(self):
        self.lark: Optional[lark.Lark] = None

    def set_grammar(self, grammar: str) -> None:
        parser = lark.Lark(grammar, propagate_positions=True)
        self.lark = parser

    def parse(self, text: str) -> lark.Tree:
        return self.lark.parse(text)
