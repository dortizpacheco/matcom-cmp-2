from cmp.pycompiler import Grammar

from .import ProgramNode
from .import ClassDeclarationNode, FuncDeclarationNode, AttrDeclarationNode
from .import LetNode, IfNode, WhileNode, BlocksNode, CaseNode, AssignNode
from .import VarDeclarationNode, SingleCaseNode
from .import CallNode, InstanceCallNode, ParentCallNode
from .import InstantiateNode,ConstantNumNode,VariableNode
from .import NotNode, ComplementNode, IsVoidNode
from .import EqualsNode, GreatNode, EqualsGreatNode
from .import PlusNode, MinusNode, StarNode, DivNode

def COOL_grammar():
    # grammar
    G = Grammar()

    # non-terminals
    program = G.NonTerminal('<program>', startSymbol=True)
    class_list, def_class = G.NonTerminals('<class-list> <def-class>')
    feature_list, def_attr, def_func = G.NonTerminals('<feature-list> <def-attr> <def-func>')
    param_list, param, expr_list = G.NonTerminals('<param-list> <param> <expr-list>')
    expr, arith, term, factor, atom = G.NonTerminals('<expr> <arith> <term> <factor> <atom>')
    func_call, arg_list  = G.NonTerminals('<func-call> <arg-list>')
    let_body,case_body = G.NonTerminals('<let-body> <case-body>')
    assig, negat, cmpx, is_void, compl, insta_func = G.NonTerminals('<assig> <negat> <cmp> <isvoid> <compl> <insta_func>')

    # terminals
    classx, let, inx, inherits = G.Terminals('class let in inherits')
    semi, colon, comma, dot, opar, cpar, ocur, ccur, _arrow, arrow = G.Terminals('; : , . ( ) { } <- =>')
    equal, plus, minus, star, div = G.Terminals('= + - * /')
    idx, num, new = G.Terminals('id int new')
    ifx, then, elsex, fi = G.Terminals('if then else fi')
    whilex, loop, pool = G.Terminals('while loop pool')
    casex, of, esac = G.Terminals('case of esac')
    notx, tilde, great, egreat, isvoid, a = G.Terminals('not ~ < <= isvoid @')
    
    #productions
    program %= class_list, lambda h,s: ProgramNode(s[1])

    class_list %= def_class + class_list, lambda h,s: [ s[1] ] + s[2]
    class_list %= G.Epsilon, lambda h,s: []

    def_class %= classx + idx + ocur + feature_list + ccur, lambda h,s: ClassDeclarationNode( s[2], s[4] )
    def_class %= classx + idx + inherits + idx + ocur + feature_list + ccur, lambda h,s: ClassDeclarationNode( s[2], s[6], s[4] )

    feature_list %= def_attr + semi + feature_list, lambda h,s: [ s[1] ] + s[2]
    feature_list %= def_func + semi + feature_list, lambda h,s: [ s[1] ] + s[2]
    feature_list %= G.Epsilon, lambda h,s: []

    def_attr %= idx + colon + idx, lambda h,s: AttrDeclarationNode( s[1], s[3] )
    def_attr %= idx + colon + idx + _arrow + expr, lambda h,s: AttrDeclarationNode( s[1], s[3], s[5] )
    def_func %= idx + opar + param_list + cpar + colon + idx + ocur + expr + ccur, lambda h,s: FuncDeclarationNode( s[1], s[3], s[6], s[8] ) 

    param_list %= param, lambda h,s: [ s[1] ]
    param_list %= param + comma + param_list, lambda h,s: [ s[1] ] + s[3]
    param_list %= G.Epsilon, lambda h,s: []

    param %= idx + colon + idx, lambda h,s: ( s[1], s[3] )

    expr %= let + let_body + inx + expr, lambda h,s: LetNode( s[2], s[4] )
    expr %= ifx + expr + then + expr + elsex + expr + fi, lambda h,s: IfNode( s[2], s[4], s[6])
    expr %= whilex + expr + loop + expr + pool, lambda h,s: WhileNode( s[2], s[4] )
    expr %= ocur + expr_list + ccur, lambda h,s: BlocksNode( s[2] )
    expr %= casex + expr + of + case_body + esac, lambda h,s: CaseNode( s[2], s[4] )
    expr %= assig, lambda h,s: s[1]

    expr_list %= expr + semi + expr_list, lambda h,s: [ s[1] ] + s[3]
    expr_list %= G.Epsilon, lambda h,s: [] 

    let_body %= idx + colon + idx + comma + let_body, lambda h,s: [ VarDeclarationNode( s[1], s[3] ) ] + s[5]
    let_body %= idx + colon + idx + _arrow + expr + comma + let_body, lambda h,s: [ VarDeclarationNode( s[1], s[3], s[5] ) ] + s[7]
    let_body %= G.Epsilon, lambda h,s: []

    case_body %= idx + colon + idx + semi + case_body, lambda h,s: [ SingleCaseNode( s[1], s[3] ) ] + s[5]
    case_body %= idx + colon + idx + arrow + expr + semi + case_body, lambda h,s: [ SingleCaseNode( s[1], s[3], s[5] ) ] + s[7]
    case_body %= G.Epsilon, lambda h,s: []

    assig %= idx + _arrow + assig, lambda h,s: AssignNode( s[1], s[3] )
    assig %= negat, lambda h,s: s[1]

    negat %= notx + negat, lambda h,s: NotNode(s[2])
    negat %= cmpx, lambda h,s: s[1]

    cmpx %= cmpx + great + cmpx, lambda h,s: GreatNode( s[1], s[3] )
    cmpx %= cmpx + egreat + cmpx, lambda h,s: EqualsGreatNode( s[1], s[3] )
    cmpx %= cmpx + equal + cmpx, lambda h,s: EqualsNode( s[1], s[3] )
    cmpx %= arith, lambda h,s: s[1]

    arith %= arith + plus + term, lambda h,s: PlusNode( s[1], s[3] )
    arith %= arith + minus + term, lambda h,s: MinusNode( s[1], s[3] )
    arith %= term, lambda h,s: s[1]

    term %= term + star + factor, lambda h,s: StarNode( s[1], s[3] )
    term %= term + div + factor, lambda h,s: DivNode( s[1], s[3] )
    term %= factor, lambda h,s: s[1]

    factor %= isvoid + factor, lambda h,s: IsVoidNode( s[2] )
    factor %= is_void, lambda h,s: s[1]

    is_void %= tilde + is_void, lambda h,s: ComplementNode( s[2] )
    is_void %= compl, lambda h,s: s[1]
    is_void %= num, lambda h,s: ConstantNumNode( s[1] )

    compl %= compl + a + idx + dot + func_call, lambda h,s: ParentCallNode( s[1], s[3], s[5][1], s[5][2] )
    compl %= insta_func, lambda h,s: s[1]

    insta_func %= insta_func + dot + func_call, lambda h,s: InstanceCallNode( s[1], s[3][1], s[3][2] )
    insta_func %= atom, lambda h,s: s[1]

    atom %= func_call, lambda h,s: CallNode( s[1][1], s[1][2] )
    atom %= opar + expr + cpar, lambda h,s: s[2]
    atom %= idx, lambda h,s: VariableNode( s[1] )
    atom %= new + idx + opar + cpar, lambda h,s: InstantiateNode(s[2])

    func_call %= idx + opar + arg_list + cpar, lambda h,s: ( s[1], s[3] )
    arg_list %= expr, lambda h,s: [ s[1] ]
    arg_list %= expr + comma + arg_list, lambda h,s: [ s[1] ] + s[3]

    return G

