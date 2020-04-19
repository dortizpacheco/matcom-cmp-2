class ParsingError(Exception):
    def __init__(self,errors):
        self.errors = errors


from .main import get_LL,get_LR
from .firts_and_follows import get_firsts_and_follow
from .ll1 import LL1

