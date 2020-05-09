from api import COOL_grammar, grammar_for_regex 
from api import COOL_regex
from api import LL1, LR1, get_firsts_and_follow, evaluate_reverse_parse
from api import Lexer, Regex

###################################  PUBLIC  ###############################################################
def run(text):
    pass
###################################  PRIVATE  ##############################################################
def lexer(text):
    G,symbol = grammar_for_regex()
    fi,fo = get_firsts_and_follow(G)
    ll1 = LL1(G, fi, fo)
    regex = Regex(G, symbol, ll1)
    table = COOL_regex()
    lexer = Lexer(table, regex, "eof")
    return lexer(text)

def parser(tokens):
    G = COOL_grammar()
    lr = LR1(G)
    return lr(tokens)

def ast(right_parse, operations, tokens):
    return evaluate_reverse_parse(right_parse,operations,tokens)

###################################  TEST  #################################################################
def unit_testing():
    pass

def unit_testing_lexer(case):
    text = case.text
    result = case.test_lexer()
    tokens = lexer(text)
    assert tokens == result

def unit_testing_parser(case):
    tokens = case.tokens
    result = case.test_parser()
    rp, opr = parser(tokens)
    assert rp == result

def unit_testing_ast(case):
    rp = case.right_parse
    opr = case.operations
    tokens = case.tokens
    result = case.test_ast()
    ast = ast(rp, opr, tokens)
    assert tokens == result