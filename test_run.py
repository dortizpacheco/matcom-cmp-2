from api import parser as api_parser
from api.lexer import automata,lexer

def check_test(work):
    print(f"================  {work} OK  ===================")

def head(work):
    print(f"<><><><><><><><><><><><><>  TEST {work}  <><><><><><><><><><><><><><><><><><><>")

head("api.parser")

check_test( api_parser.firts_and_follows.unit_testing() )
check_test( api_parser.ll1.unit_testing() )

head("api.lexer")

check_test( automata.unit_testing() )

check_test( lexer.unit_testing() )