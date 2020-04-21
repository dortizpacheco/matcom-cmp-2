from .main import get_lexer
from .automata import nfa_to_dfa, grammar_for_regex

from api.parser import LL1, get_firsts_and_follow

class Parser:
    def __init__(self,G):
        f,ff = get_firsts_and_follow(G)
        self.func = LL1(G,f,ff)
    def __call__(self,text):
        return self.func(text,True)