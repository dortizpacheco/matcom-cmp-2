from cmp.utils import Token
from cmp.automata import State
from .import nfa_to_dfa

# import for testing
from .import Parser, grammar_for_regex
###################################  PUBLIC  ###############################################################
class Regex:
    """
        G is grammar of cmp
        symbol is name of symbol terminal of grammar G
        parser func that return func that resive text and return ast
    """
    def __init__(self, G, symbol, parser):
        self.G = G
        self.parser = parser(G)
        self.symbol = symbol

    def __call__(self,regular_exp):
        tokens = _regex_tokenizer(self.G, self.symbol,  regular_exp)
        ast = self.parser(tokens)
        return nfa_to_dfa(ast.evaluate())

class Lexer:
    def __init__(self, table, regex, eof):
        self.eof = eof
        self.regex = regex
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()
    
    def __call__(self, text):
        errors = []
        return [ Token(lex, ttype) for lex, ttype in self._tokenize(text,errors) ], errors
###################################  PRIVATE  ##############################################################
    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, text_regex) in enumerate(table):
            automaton = State.from_nfa(self.regex(text_regex))
            for state in automaton:
                if state.final: state.tag = (n, token_type)

            regexs.append(automaton)
        return regexs

    def _build_automaton(self):
        start = State('start')
        for automaton in self.regexs:
            start.add_epsilon_transition(automaton)
        return start.to_deterministic()

    def _walk(self, string):
        state = self.automaton
        final = state 
        final_lex = lex = ''

        for symbol in string:
            try:
                lex += symbol
                state = state[symbol][0]
                if state.final:
                    final = state
                    final_lex = lex
            except:
                if final_lex == '': raise LexerError(lex)
                break
    
        return final_lex, final

    def _tokenize(self, _text, errors):
        text = _text
        final = None

        while len(text) > 0:
            try:
                final_lex, final= self._walk(text)
            except LexerError as e:
                errors.append(e.error)
                text = text[len(e.error):]
                continue

            minPrior = -1
            finalfinal = None

            for st in final.state:
                if st.final:
                    n, _ = st.tag
                    if  minPrior == -1 or n < minPrior:
                        minPrior = n
                        finalfinal = st           
    
            yield final_lex, finalfinal.tag[1]
            text = text[len(final_lex):]
    
        yield '$', self.eof

class LexerError(Exception):
    def __init__(self,error):
        self.error = error 

def _regex_tokenizer(G, symbol, text, skip_whitespaces=False):
    tokens = []
    if len(text) == 1:
        tokens.append(Token(text[0],G[symbol]))
    else: 
        for char in text:
            if skip_whitespaces and char.isspace():
                continue
            temp = G[char]
            if not temp is None:
                tokens.append(Token(char, temp))
            else:
                tokens.append(Token(char, G[symbol]))
    
    tokens.append(Token('$', G.EOF))
    return tokens
###################################  TEST  ##################################################################

def unit_testing():
    __unit_testing_regex_tokenizer()
    print(" - tokenizer regex ;)")
    __test_regax()
    print(" - regex           ;)")
    lexer = __test_lexer()
    print(" - builder lexer   ;)")
    __test_lexer_2(lexer)
    print(" - lexer           ;)")

 
    return "LEX"

def __unit_testing_regex_tokenizer():
    G,symbol = grammar_for_regex()
    tokens = _regex_tokenizer(G,symbol,"a*(a|b)*cd|ε")
    assert tokens == [
        Token("a",G[symbol]),
        Token("*",G["*"]),
        Token("(",G["("]),
        Token("a",G[symbol]),
        Token("|",G["|"]),
        Token("b",G[symbol]),
        Token(")",G[")"]),
        Token("*",G["*"]),
        Token("c",G[symbol]),
        Token("d",G[symbol]),
        Token("|",G["|"]),
        Token("ε",G["ε"]),
        Token("$",G.EOF)
    ], "regex tokenizer error in 'a*(a|b)*cd|ε'"
    tokens = _regex_tokenizer(G,symbol,"*")
    assert tokens == [ Token("*",G[symbol]),
                       Token("$",G.EOF)
    ], "regex tokenizer error in '*'"

def __test_regax():
    G,symbol = grammar_for_regex()
    dfa = nfa_to_dfa( Regex(G,symbol,Parser)("a*(a|b)*cd|ε") )

    assert dfa.recognize(''), "Regex error in '' "
    assert dfa.recognize('cd'), "Regex error in 'cd' "
    assert dfa.recognize('aaaaacd'), "Regex error in 'aaaaacd' "
    assert dfa.recognize('bbbbbcd'), "Regex error in 'bbbbbcd' "
    assert dfa.recognize('bbabababcd'), "Regex error in 'bbabababcd' "
    assert dfa.recognize('aaabbabababcd'), "Regex error in 'aaabbabababcd' "
    assert not dfa.recognize('cda'), "Regex error in not 'cda' "
    assert not dfa.recognize('aaaaa'), "Regex error in not 'aaaaa' "
    assert not dfa.recognize('bbbbb'), "Regex error in not 'bbbbb' "
    assert not dfa.recognize('ababba'), "Regex error in not 'ababba' "
    assert not dfa.recognize('cdbaba'), "Regex error in not 'cdbaba' "
    assert not dfa.recognize('cababad'), "Regex error in not 'cababad' "
    assert not dfa.recognize('bababacc'), "Regex error in not 'bababacc' "

def __test_lexer():
    nonzero_digits = '|'.join(str(n) for n in range(1,10))
    letters = '|'.join(chr(n) for n in range(ord('a'),ord('z')+1))

    G,symbol = grammar_for_regex()
    regex = Regex(G,symbol,Parser)

    lexer = Lexer([
        ('num', f'({nonzero_digits})(0|{nonzero_digits})*'),
        ('for' , 'for'),
        ('foreach' , 'foreach'),
        ('space', ' *'),
        ('id', f'({letters})({letters}|0|{nonzero_digits})*')
    ], regex, 'eof')

    assert not lexer is None, "Lexer not builder"

    return lexer

def __test_lexer_2(lexer):
    text = '5465 for 45foreach fore'
    tokens,errors = lexer(text)
    assert errors == []
    assert [t.token_type for t in tokens] == ['num', 'space', 'for', 'space', 'num', 'foreach', 'space', 'id', 'eof']
    assert [t.lex for t in tokens] == ['5465', ' ', 'for', ' ', '45', 'foreach', ' ', 'fore', '$']

    text = '4forense forforeach for4foreach foreach 4for'
    tokens,errors = lexer(text)
    assert errors == []
    assert [t.token_type for t in tokens] == ['num', 'id', 'space', 'id', 'space', 'id', 'space', 'foreach', 'space', 'num', 'for', 'eof']
    assert [t.lex for t in tokens] == ['4', 'forense', ' ', 'forforeach', ' ', 'for4foreach', ' ', 'foreach', ' ', '4', 'for', '$']

    text = "LAexer"
    tokens,errors = lexer(text)
    assert errors == ["L","A"]
    assert tokens == [ Token("exer","id"),
                       Token("$", "eof")
    ]
