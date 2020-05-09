from cmp.tools.parsing import LR1Parser as LR1
from cmp.evaluation import evaluate_reverse_parse
from cmp.pycompiler import Grammar
###################################  PUBLIC  ###############################################################

###################################  PRIVATE  ##############################################################
###################################  TEST  #################################################################

def unit_testing():
    G = Grammar()
    E = G.NonTerminal('E', True)
    A = G.NonTerminal('A')
    equal, plus, num = G.Terminals('= + int')

    E %=  A + equal + A | num
    A %= num + plus + A | num

    parser = LR1(G)
    derivation = parser([num, plus, num, equal, num, plus, num, G.EOF])

    assert str(derivation) == '[A -> int, A -> int + A, A -> int, A -> int + A, E -> A = A]'
    return "LR1"