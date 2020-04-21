import pydot
from cmp.pycompiler import Grammar
from cmp.ast_abstract_node import AtomicNode,UnaryNode,BinaryNode
from cmp.utils import ContainerSet
from cmp.utils import DisjointSet 

###################################  PUBLIC  ###############################################################

class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = { state: {} for state in range(states) }
        
        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)
            
        self.vocabulary.discard('')
        
    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return ()
            
    def graph(self):
        G = pydot.Dot(rankdir='LR', margin=0.1)
        G.add_node(pydot.Node('start', shape='plaintext', label='', width=0, height=0))

        for (start, tran), destinations in self.map.items():
            tran = 'ε' if tran == '' else tran
            G.add_node(pydot.Node(start, shape='circle', style='bold' if start in self.finals else ''))
            for end in destinations:
                G.add_node(pydot.Node(end, shape='circle', style='bold' if end in self.finals else ''))
                G.add_edge(pydot.Edge(start, end, label=tran, labeldistance=2))

        G.add_edge(pydot.Edge('start', self.start, label='', style='dashed'))
        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except:
            pass

class DFA(NFA):
    
    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)
        
        transitions = { key: [value] for key, value in transitions.items() }
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start
        
    def _move(self, symbol):
        try:
            self.current = self.transitions[self.current][symbol][0]
            return True
        except KeyError:
            return False
            
    def _reset(self):
        self.current = self.start
        
    def recognize(self, string):
        self._reset()
        for item in string:
            if not self._move(item):
                return False
        
        return self.current in self.finals

'''
    the param terminals is str with formatte:
    pipe closure ( ) symbol epsilon
'''
def grammar_for_regex(terminals = '| * ( ) symbol ε' ):
    G_for_regular_exp = Grammar()
    E = G_for_regular_exp.NonTerminal('E', True)
    T, F, A, X, Y, Z = G_for_regular_exp.NonTerminals('T F A X Y Z')
    pipe, star, opar, cpar, symbol, epsilon = G_for_regular_exp.Terminals(terminals)

    E %= T + X,                     lambda h,s:s[2], None, lambda h,s: s[1]

    X %= pipe + T + X,              lambda h,s: s[3], None, None, lambda h,s: UnionNode(h[0], s[2])
    X %= G_for_regular_exp.Epsilon, lambda h,s: h[0]

    T %= F + Y,                     lambda h,s: s[2], None, lambda h,s: s[1]

    Y %= F + Y,                     lambda h,s: s[2], None, lambda h,s: ConcatNode(h[0], s[1])
    Y %= G_for_regular_exp.Epsilon, lambda h,s: h[0]

    F %= A + Z,                     lambda h,s: s[2], None, lambda h,s: s[1]

    Z %= star + Z,                  lambda h,s: s[2], None, lambda h,s: ClosureNode(h[0])
    Z %= G_for_regular_exp.Epsilon, lambda h,s: h[0]

    A %= opar + E + cpar ,          lambda h,s: s[2], None, None, None
    A %= symbol,                    lambda h,s: SymbolNode(s[1]), None
    A %= epsilon,                   lambda h,s: EpsilonNode(h[0])

    return G_for_regular_exp, symbol.Name

def nfa_to_dfa(automaton):
    transitions = {}
    
    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [ start ]
    
    pending = [ start ]
    while pending:
        state = pending.pop()
     
        for symbol in automaton.vocabulary:

            e_closure = ContainerSet(*move(automaton,state,symbol))
            e_closure.update(epsilon_closure(automaton,e_closure.set))
                
            if(len(e_closure) == 0):
                continue
                
            try:
                transitions[state.id,symbol] = states[states.index(e_closure)].id
            except ValueError:
                e_closure.id = len(states)
                e_closure.is_final = any(s in automaton.finals for s in e_closure)
                states.append(e_closure)
                pending.append(e_closure)
                transitions[state.id,symbol] = e_closure.id
    
    finals = [ state.id for state in states if state.is_final ]
    dfa = DFA(len(states), finals, transitions)
    return dfa

def automata_minimization(automaton):
    partition = state_minimization(automaton)
    
    states = [s for s in partition.representatives]
    mapper = { state : int(i) for i,state in enumerate(states) }
    
    transitions = {}
    for i, state in enumerate(states):
        #transitions[i] = {}
        for symbol, destinations in automaton.transitions[state.value].items():
            transitions[i,symbol] = [ mapper[partition[n].representative] for n in destinations ][0]
    
    finals = [ mapper[partition[n].representative] for n in automaton.finals ]
    start  = mapper[partition[automaton.start].representative]
    
    return DFA(len(states), finals, transitions, start)
###################################  PRIVATE  ##############################################################

""" AST REGEX """
class EpsilonNode(AtomicNode):
    def evaluate(self):
        return NFA(1,[0],{})

class SymbolNode(AtomicNode):
    def evaluate(self):
        s = self.lex
        return NFA(2,[1],{(0,s):[1]})

class ClosureNode(UnaryNode):
    @staticmethod
    def operate(value):
        return automata_closure(value)

class UnionNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return automata_union(lvalue,rvalue)

class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return automata_concatenation(lvalue,rvalue)

""" ALGEBRA TO AUTOMATA """
def automata_closure(a1):
    transitions = {}
    
    start = 0
    d1 = 1
    final = a1.states + d1
    
    for (origin, symbol), destinations in a1.map.items():
        transitions[origin + d1 , symbol] = [ nd + d1 for nd in destinations]
        
    transitions[start , ''] = [ d1 , final]
    
    for state in a1.finals:
        transitions[state + d1, ''] = [a1.start + d1 ,final]
    
    states = a1.states +  2
    finals = { final }
    
    return NFA(states, finals, transitions, start)

def automata_union(a1, a2):
    transitions = {}
    
    start = 0
    d1 = 1
    d2 = a1.states + d1
    final = a2.states + d2
    
    for (origin, symbol), destinations in a1.map.items():
        transitions[origin + d1 , symbol] = [nd + d1 for nd in destinations]

    for (origin, symbol), destinations in a2.map.items():
        transitions[origin + d2 , symbol] = [nd + d2 for nd in destinations]
    
    transitions[start,''] = [d1,d2]
    
    for state in a1.finals:
        transitions[state + d1,''] = [final]
    for state in a2.finals:
        transitions[state + d2,''] = [final]
        
    states = a1.states + a2.states + 2
    finals = { final }
    
    return NFA(states, finals, transitions, start)
    
def automata_concatenation(a1, a2):
    transitions = {}
    
    start = 0
    d1 = 0
    d2 = a1.states + d1
    final = a2.states + d2
    
    for (origin, symbol), destinations in a1.map.items():
        transitions[origin + d1 , symbol] = [nd + d1 for nd in destinations]
        
    for (origin, symbol), destinations in a2.map.items():
        transitions[origin + d2 , symbol] = [nd + d2 for nd in destinations]
    
    for state in a1.finals:
        transitions[state + d1,''] = [d2]
    for state in a2.finals:
        transitions[state + d2,''] = [final]
    
    states = a1.states + a2.states + 1
    finals = { final }
    
    return NFA(states, finals, transitions, start)

""" TRASFORM TO AUTOMATA """
def move(automaton, states, symbol):
    moves = set()
    for state in states:
        try:
            for item in automaton.transitions[state][symbol]:
                moves.add(item)
        except KeyError:
            pass
    return moves

def epsilon_closure(automaton, states):
    pending = [ s for s in states ] # equivalente a list(states) pero me gusta así :p
    closure = { s for s in states } # equivalente a  set(states) pero me gusta así :p
    
    while pending:
        state = pending.pop()
        try:
            for item in automaton.transitions[state]['']:
                pending.append(item)
                closure.add(item)
        except KeyError:
            pass
                
    return ContainerSet(*closure)

""" MINIMIZATION TO AUTOMATA """
def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))
    
    not_final = {s for s in range(automaton.states)}
    final = {s for s in automaton.finals}
    not_final.difference_update(final)
    
    partition.merge(not_final)
    partition.merge(final)
    
    while True:
        new_partition = DisjointSet(*range(automaton.states))
            
        for group in partition.groups:
            new_groups = distinguish_states(group,automaton,partition)
            for g in new_groups:
                new_partition.merge(g)

        if len(new_partition) == len(partition):
            break

        partition = new_partition
        
    return partition

def distinguish_states(group, automaton, partition):
    split = {}
    vocabulary = tuple(automaton.vocabulary)

    for member in group:
        new_group = []
        for symbol in vocabulary:
            try:
                ikey = partition[automaton.transitions[member.value][symbol][0]].representative
                new_group.append(ikey)
            except KeyError:
                new_group.append(None)
        try:
            split[tuple(new_group)].append(member.value)
        except KeyError:
            split[tuple(new_group)] = [member.value]
            
    return [ group for group in split.values()]

###################################  TEST  #################################################################

def unit_testing():
    __test_dfa()
    print(" - dfa                ;) ")
    __test_trasform_move()
    print(" - move               ;) ")
    __test_trasform_epsilon_closure()
    print(" - epsilon closure    ;) ")
    __test_nfa_to_dfa()
    print(" - nfa to dfa         ;) ")
    __test_algebra_union()
    print(" - union              ;) ")
    __test_algebra_closure()
    print(" - closure            ;) ")
    __test_algebra_concatenation()
    print(" - concatenation      ;) ")
    __test_minimization_state()
    print(" - minimization state ;) ")
    __test_minimization_automata()
    print(" - mini automata      ;) ")

    return "ATM"

def __test_dfa():
    automaton = DFA(states=3, finals=[2], transitions={
        (0, 'a'): 0,
        (0, 'b'): 1,
        (1, 'a'): 2,
        (1, 'b'): 1,
        (2, 'a'): 0,
        (2, 'b'): 1,
    })

    assert automaton.recognize('ba')
    assert automaton.recognize('aababbaba')

    assert not automaton.recognize('')
    assert not automaton.recognize('aabaa')
    assert not automaton.recognize('aababb')

def __test_trasform_move():
    automaton = NFA(states=6, finals=[3, 5], transitions={
        (0, ''): [ 1, 2 ],
        (1, ''): [ 3 ],
        (1,'b'): [ 4 ],
        (2,'a'): [ 4 ],
        (3,'c'): [ 3 ],
        (4, ''): [ 5 ],
        (5,'d'): [ 5 ]
    })
    
    assert move(automaton, [1], 'a') == set()
    assert move(automaton, [2], 'a') == {4}
    assert move(automaton, [1, 5], 'd') == {5}

def __test_trasform_epsilon_closure():
    automaton = NFA(states=6, finals=[3, 5], transitions={
        (0, ''): [ 1, 2 ],
        (1, ''): [ 3 ],
        (1,'b'): [ 4 ],
        (2,'a'): [ 4 ],
        (3,'c'): [ 3 ],
        (4, ''): [ 5 ],
        (5,'d'): [ 5 ]
    })
    assert epsilon_closure(automaton, [0]) == {0,1,2,3}
    assert epsilon_closure(automaton, [0, 4]) == {0,1,2,3,4,5}
    assert epsilon_closure(automaton, [1, 2, 4]) == {1,2,3,4,5}

def __test_nfa_to_dfa():
    automaton = NFA(states=6, finals=[3, 5], transitions={
        (0, ''): [ 1, 2 ],
        (1, ''): [ 3 ],
        (1,'b'): [ 4 ],
        (2,'a'): [ 4 ],
        (3,'c'): [ 3 ],
        (4, ''): [ 5 ],
        (5,'d'): [ 5 ]
    })

    dfa = nfa_to_dfa(automaton)

    assert dfa.states == 4
    assert len(dfa.finals) == 4

    assert dfa.recognize('')
    assert dfa.recognize('a')
    assert dfa.recognize('b')
    assert dfa.recognize('cccccc')
    assert dfa.recognize('adddd')
    assert dfa.recognize('bdddd')

    assert not dfa.recognize('dddddd')
    assert not dfa.recognize('cdddd')
    assert not dfa.recognize('aa')
    assert not dfa.recognize('ab')
    assert not dfa.recognize('ddddc')

def __test_algebra_union():
    automaton = DFA(states=2, finals=[1], transitions={
        (0,'a'):  0,
        (0,'b'):  1,
        (1,'a'):  0,
        (1,'b'):  1,
    })
    union = automata_union(automaton, automaton)
    recognize = nfa_to_dfa(union).recognize

    assert union.states == 2 * automaton.states + 2
    assert recognize('b')
    assert recognize('abbb')
    assert recognize('abaaababab')
    assert not recognize('')
    assert not recognize('a')
    assert not recognize('abbbbaa')

def __test_algebra_concatenation():
    automaton = DFA(states=2, finals=[1], transitions={
        (0,'a'):  0,
        (0,'b'):  1,
        (1,'a'):  0,
        (1,'b'):  1,
    })
    concat = automata_concatenation(automaton, automaton)
    recognize = nfa_to_dfa(concat).recognize

    assert concat.states == 2 * automaton.states + 1
    assert recognize('bb')
    assert recognize('abbb')
    assert recognize('abaaababab')
    assert not recognize('')
    assert not recognize('a')
    assert not recognize('b')
    assert not recognize('ab')
    assert not recognize('aaaab')
    assert not recognize('abbbbaa')

def __test_algebra_closure():
    automaton = DFA(states=2, finals=[1], transitions={
        (0,'a'):  0,
        (0,'b'):  1,
        (1,'a'):  0,
        (1,'b'):  1,
    })
    closure = automata_closure(automaton)
    recognize = nfa_to_dfa(closure).recognize

    assert closure.states == automaton.states + 2
    assert recognize('')
    assert recognize('b')
    assert recognize('ab')
    assert recognize('bb')
    assert recognize('abbb')
    assert recognize('abaaababab')
    assert not recognize('a')
    assert not recognize('abbbbaa')

def __test_minimization_state():
    automaton = DFA(states=5, finals=[4], transitions={
        (0,'a'): 1,
        (0,'b'): 2,
        (1,'a'): 1,
        (1,'b'): 3,
        (2,'a'): 1,
        (2,'b'): 2,
        (3,'a'): 1,
        (3,'b'): 4,
        (4,'a'): 1,
        (4,'b'): 2,
    })

    states = state_minimization(automaton)

    for members in states.groups:
        all_in_finals = all(m.value in automaton.finals for m in members)
        none_in_finals = all(m.value not in automaton.finals for m in members)
        assert all_in_finals or none_in_finals

    assert len(states) == 4
    assert states[0].representative == states[2].representative
    assert states[1].representative == states[1]
    assert states[3].representative == states[3]
    assert states[4].representative == states[4]

def __test_minimization_automata():
    automaton = DFA(states=5, finals=[4], transitions={
        (0,'a'): 1,
        (0,'b'): 2,
        (1,'a'): 1,
        (1,'b'): 3,
        (2,'a'): 1,
        (2,'b'): 2,
        (3,'a'): 1,
        (3,'b'): 4,
        (4,'a'): 1,
        (4,'b'): 2,
    })
    mini = automata_minimization(automaton)

    assert mini.states == 4
    assert mini.recognize('abb')
    assert mini.recognize('ababbaabb')
    assert not mini.recognize('')
    assert not mini.recognize('ab')
    assert not mini.recognize('aaaaa')
    assert not mini.recognize('bbbbb')
    assert not mini.recognize('abbabababa')