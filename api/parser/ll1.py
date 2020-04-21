from cmp.utils import Token
from .import ParsingError

#import for unit testing
from cmp.pycompiler import Symbol,NonTerminal,Terminal,Sentence,SentenceList,EOF,Epsilon,Grammar,Production
from cmp.languages import BasicXCool
###################################  PUBLIC  ###############################################################

class LL1:
    def __init__(self, G, firsts, follow):
        self.grammar = G
        self.table = _build_parsing_table(G,firsts,follow)
    
    def __call__(self, tokens, _eval = False):
        parser = _buid_parsing_func(self.grammar, self.table)
        left_parse,error = parser(tokens)
        if len(error) != 0: raise ParsingError(error)
        if not _eval: return left_parse

        return _evaluate_parse(left_parse,tokens)

###################################  PRIVATE  ##############################################################

'''
    compute table' LL1 for the G grammar that has the property Productions list
    whe Productions is list that has property Left and Right
    firsts and follow is dic of sets that has property contains_epsilon
'''
def _build_parsing_table(G, firsts, follows):
    M = {}
    
    for production in G.Productions:
        X = production.Left
        alpha = production.Right
        
        for t in firsts[alpha]:
            try:
                M[X,t].append(production)
            except KeyError:
                M[X,t] = [production]
        
        if firsts[alpha].contains_epsilon: 
            for t in follows[X]:
                try:
                    M[X,t].append(production)
                except KeyError:
                    M[X,t] = [production]
    
    return M   

'''
    compute if list tokens in lenguage of grammar G, using M table for parsing LL1
    G has property EOF,startSymbol,
    tokens is string list
    M is dic of nonTerminal,current_token vs production, this productions has property Right
'''
def _buid_parsing_func(G,M):
    def parser(tokens):
        if len(tokens) > 0 and isinstance(tokens[0],Token): 
            tokens = [t.token_type for t in tokens]

        stack = [G.EOF,G.startSymbol]
        cursor = 0
        output = []
        error = []
        top = None

        while top != G.EOF:
            top = stack.pop()
            current_token = tokens[cursor]

            if top.IsTerminal: 
                if top != current_token:
                    error.append(f'parsing error: in the top is {top} and currend tokens is {current_token}')
                else:
                    cursor += 1
            elif top.IsNonTerminal:
                try:
                    production = M[top,current_token][0]
                    alpha = production.Right

                    output.append(production)
                    i = len(alpha) - 1 
                    while i != -1:
                        stack.append(alpha[i])
                        i -= 1 
                except KeyError:
                    error.append(f"parsing error: the grammer don't know what doing with {top} when find one {current_token}")

        return output,error
    return parser


def _evaluate_parse(left_parse, tokens):
    if not left_parse or not tokens:
        return
    
    left_parse = iter(left_parse)
    tokens = iter(tokens)
    result = __evaluate(next(left_parse), left_parse, tokens)
    
    assert isinstance(next(tokens).token_type, EOF)
    return result
    
def __evaluate(production, left_parse, tokens, inherited_value=None):
    _ , body = production
    attributes = production.attributes
    
    
    synteticed = [None]*(len(body) + 1)
    inherited = [None]*(len(body) + 1)
    inherited[0] = inherited_value

    for i, symbol in enumerate(body, 1):
        if symbol.IsTerminal:
            assert inherited[i] is None
            token = next(tokens)
            synteticed[i] = token.lex
        else:
            next_production = next(left_parse)
            assert symbol == next_production.Left
            if not attributes[i] is None:
                inherited[i] = attributes[i](inherited,synteticed)
            synteticed[i] = __evaluate(next_production,left_parse,tokens,inherited[i])
            
    return attributes[0](inherited,synteticed)

###################################  TEST  #################################################################

def unit_testing():
    G = Grammar()
    E = G.NonTerminal('E', True)
    T,F,X,Y = G.NonTerminals('T F X Y')
    plus, minus, star, div, opar, cpar, num = G.Terminals('+ - * / ( ) num')

    E %= T + X, lambda h,s: s[2], None, lambda h,s: s[1]                    
    
    X %= plus + T + X, lambda h,s: s[3], None, None, lambda h,s: s[2] + h[0]
    X %= minus + T + X, lambda h,s: s[3], None, None, lambda h,s: h[0] - s[2] 
    X %= G.Epsilon, lambda h,s: h[0]                                                    
    
    T %= F + Y, lambda h,s: s[2], None, lambda h,s: s[1]                                            
    
    Y %= star + F + Y, lambda h,s: s[3], None, None, lambda h,s: h[0] * s[2]                               
    Y %= div + F + Y, lambda h,s: s[3], None, None, lambda h,s: h[0]/s[2]                                
    Y %= G.Epsilon, lambda h,s: h[0]                                                    
    
    F %= num, lambda h,s: float(s[1]), None                                                    
    F %= opar + E + cpar, lambda h,s: s[2], None, None, None     
    
    xcool = BasicXCool(G)
    tokens = [num, star, num, star, num, plus, num, star, num, plus, num, plus, num, G.EOF]

    M = _build_parsing_table(G,xcool.firsts,xcool.follows)
    assert M == xcool.table ,"Test Error in  build_parsing_table"

    print(" - buider table ;) ")

####################################################################
    parser = _buid_parsing_func(G,M)
    left_parse,error = parser(tokens)
    assert error == []
    assert left_parse == [ 
       Production(E, Sentence(T, X)),
       Production(T, Sentence(F, Y)),
       Production(F, Sentence(num)),
       Production(Y, Sentence(star, F, Y)),
       Production(F, Sentence(num)),
       Production(Y, Sentence(star, F, Y)),
       Production(F, Sentence(num)),
       Production(Y, G.Epsilon),
       Production(X, Sentence(plus, T, X)),
       Production(T, Sentence(F, Y)),
       Production(F, Sentence(num)),
       Production(Y, Sentence(star, F, Y)),
       Production(F, Sentence(num)),
       Production(Y, G.Epsilon),
       Production(X, Sentence(plus, T, X)),
       Production(T, Sentence(F, Y)),
       Production(F, Sentence(num)),
       Production(Y, G.Epsilon),
       Production(X, Sentence(plus, T, X)),
       Production(T, Sentence(F, Y)),
       Production(F, Sentence(num)),
       Production(Y, G.Epsilon),
       Production(X, G.Epsilon),
    ] ,"Test Error in  parser_library.LL1.parser"

    print(" - buider func  ;) ")

###################################################################
    fixed_tokens = {
    '+'  :   Token( '+', plus  ),
    '-'  :   Token( '-', minus ),
    '*'  :   Token( '*', star  ),
    '/'  :   Token( '/', div   ),
    '('  :   Token( '(', opar  ),
    ')'  :   Token( ')', cpar  ),
    }

    def tokenize_text(text):
        tokens = []

        for item in text.split():
            try:
                float(item)
                token = Token(item, num)
            except ValueError:
                try:
                    token = fixed_tokens[item]
                except:
                    raise Exception('Undefined token')
            tokens.append(token)

        eof = Token('$', G.EOF)
        tokens.append(eof)

        return tokens


    text = '5.9 + 4'
    tokens = [ Token('5.9', num), Token('+', plus), Token('4', num), Token('$', G.EOF) ]
    left_parse,error = parser(tokens)
    assert len(left_parse) == 9 and len(error) == 0,"Test Error in  parser func"
    result = _evaluate_parse(left_parse, tokens)
    assert result == 9.9,"Test Error in  eval parser"

    text = '1 - 1 - 1'
    tokens = tokenize_text(text)
    left_parse,error = parser(tokens)
    assert len(left_parse) == 13 and len(error) == 0,"Test Error in  parser func"
    result = _evaluate_parse(left_parse, tokens)
    assert result == -1,"Test Error in  eval parser"

    text = '1 - ( 1 - 1 )'
    tokens = tokenize_text(text)
    left_parse,error = parser(tokens)
    assert len(left_parse) == 18 and len(error) == 0,"Test Error in  parser func"
    result = _evaluate_parse(left_parse, tokens)
    assert result == 1,"Test Error in  eval parser"

    print(" - method eval  ;) ")

#############################################################
    return "LL1"


