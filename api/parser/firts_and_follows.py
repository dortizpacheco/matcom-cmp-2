from cmp.utils import ContainerSet

#import for unit testing
from cmp.pycompiler import Symbol,NonTerminal,Terminal,Sentence,SentenceList,EOF,Epsilon,Grammar,Production
from cmp.languages import BasicXCool

###################################  PUBLIC  ###############################################################

def get_firsts_and_follow(G):
    first = compute_firsts(G)
    follow = compute_follows(G,first)
    return first,follow

'''
 compute firsts sets for the G grammar that has the property terminals,nonTerminals,Productions list
 whe Productions is list that has property Left and Right
'''
def compute_firsts(G):
    firsts = {}
    change = True
    
    # init First(Vt)
    for terminal in G.terminals:
        firsts[terminal] = ContainerSet(terminal)
        
    # init First(Vn)
    for nonterminal in G.nonTerminals:
        firsts[nonterminal] = ContainerSet()
    
    while change:
        change = False
        
        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right
            
            # get current First(X)
            first_X = firsts[X]
                
            # init First(alpha)
            try:
                first_alpha = firsts[alpha]
            except:
                first_alpha = firsts[alpha] = ContainerSet()
            
            # CurrentFirst(alpha)???
            local_first = _compute_local_first(firsts, alpha)
            
            # update First(X) and First(alpha) from CurrentFirst(alpha)
            change |= first_alpha.hard_update(local_first)
            change |= first_X.hard_update(local_first)
                    
    return firsts

'''
 compute follows sets for the G grammar that has the property terminals,nonTerminals,Productions list
 whe Productions is list that has property Left and Right
'''
def compute_follows(G, firsts):
    follows = { }
    change = True
        
    # init Follow(Vn)
    for nonterminal in G.nonTerminals:
        follows[nonterminal] = ContainerSet()
    follows[G.startSymbol] = ContainerSet(G.EOF)
    
    while change:
        change = False
        
        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right
            
            follow_X = follows[X]
            
            for i,symbol in enumerate(alpha):
                if symbol.IsNonTerminal:
                    beta = alpha[i+1:]
                    first_beta = _compute_local_first(firsts,beta)
                    change |= follows[symbol].update(first_beta)
                    if first_beta.contains_epsilon or len(beta) == 0:
                        change |= follows[symbol].update(follow_X)
                    
    # Follow(Vn)
    return follows


###################################  PRIVATE  ##############################################################
# alpha == epsilon ? First(alpha) = { epsilon }
# alpha = X1 ... XN
# First(Xi) subconjunto First(alpha)
# epsilon pertenece a First(X1)...First(Xi) ? First(Xi+1) subconjunto de First(X) y First(alpha)
# epsilon pertenece a First(X1)...First(XN) ? epsilon pertence a First(X) y al First(alpha)
def _compute_local_first(firsts, alpha):
    first_alpha = ContainerSet()
    
    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except:
        alpha_is_epsilon = False
            
    if alpha_is_epsilon:
        first_alpha.set_epsilon()
        
    for symbol in alpha:
        first_alpha.update(firsts[symbol])
        if not firsts[symbol].contains_epsilon :
            break
    else:    
        first_alpha.set_epsilon()
    
    return first_alpha


###################################  TEST  #################################################################

def unit_testing():
    G = __unit_testing_get_grammar()
    xcool = BasicXCool(G)

    firsts = compute_firsts(G)
    assert firsts == xcool.firsts , "Test Error in parser_library.algorithm.firts_set.compute_firts"

    print(" - firsts  ;) ")

    follows = compute_follows(G,firsts)
    assert follows == xcool.follows , "Test Error in parser_library.algorithm.follow_set.compute_follows"
    
    print(" - follows ;) ")

    return "FAF"


def __unit_testing_get_grammar():
    G = Grammar()
    E = G.NonTerminal('E', True)
    T,F,X,Y = G.NonTerminals('T F X Y')
    plus, minus, star, div, opar, cpar, num = G.Terminals('+ - * / ( ) num')

    E %= T + X
    X %= plus + T + X | minus + T + X | G.Epsilon
    T %= F + Y
    Y %= star + F + Y | div + F + Y | G.Epsilon
    F %= num | opar + E + cpar
    return G