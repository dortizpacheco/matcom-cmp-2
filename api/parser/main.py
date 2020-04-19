from cmp.tools.parsing import LR1Parser
from cmp.evaluation import evaluate_reverse_parse


def get_LR(G):
    return LR1Parser(G)
def get_LL(G):
    pass

def ast_from(parse, operations, tokens):
    return evaluate_reverse_parse(parse, operations, tokens)