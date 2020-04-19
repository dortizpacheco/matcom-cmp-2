from api.grammar import COOL_grammar
from api.parser import get_LR
from .test_list import _list

def grammar_test():
    G = COOL_grammar()
    parse = get_LR(G)

    for text,tokens,accept in _list:
        assert parse(text,tokens) == accept






