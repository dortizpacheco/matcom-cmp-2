from api import parser as api_parser

def check_test(work):
    print(f"###################################  {work} OK  #################################################################")


check_test( api_parser.firts_and_follows.unit_testing() )
check_test( api_parser.ll1.unit_testing() )

