################# Level 0 #################################################
class Node:
    pass

################# Level 1 #################################################
class ProgramNode(Node):
    def __init__(self, declarations):
        self.declarations = declarations

class DeclarationNode(Node):
    pass
class ExpressionNode(Node):
    pass

################# Level 2 #################################################
class ClassDeclarationNode(DeclarationNode):
    def __init__(self, idx, features, parent=None):
        self.id = idx
        self.parent = parent
        self.features = features

class FuncDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, return_type, body):
        self.id = idx
        self.params = params
        self.type = return_type
        self.body = body

class AttrDeclarationNode(DeclarationNode):
    def __init__(self, idx, typex, expr = None):
        self.id = idx
        self.type = typex
        self.expr = expr 

################# "Statement" Level 3 #################################################
class LetNode(ExpressionNode):
    def __init__(self, list_var_declaration, expr):
        self.list = list_var_declaration
        self.expr = expr

class IfNode(ExpressionNode):
    def __init__(self, condiction, then, _else):
        self.condiction = condiction
        self.then = then
        self._else = _else

class WhileNode(ExpressionNode):
    def __init__(self, condiction, body):
        self.condiction = condiction
        self.body = body

class BlocksNode(ExpressionNode):
    def __init__(self, _list):
        self._list = _list

class CaseNode(ExpressionNode):
    def __init__(self, expr, case_list):
        self.expr = expr
        self.case_list = case_list

class AssignNode(ExpressionNode):
    def __init__(self, idx, expr):
        self.id = idx
        self.expr = expr

################# Complement Level 3 #################################################
class VarDeclarationNode(ExpressionNode):
    def __init__(self, idx, typex, expr = None):
        self.id = idx
        self.type = typex
        self.expr = expr

class SingleCaseNode(ExpressionNode):
    def __init__(self, idx, typex, expr = None):
        self.id = idx
        self.type = typex
        self.expr = expr

################# Call Level 4 #################################################
class CallNode(ExpressionNode):
    def __init__(self, idx, args):
        self.id = idx
        self.args = args

class InstanceCallNode(ExpressionNode):
    def __init__(self, obj, idx, args):
        self.obj = obj
        self.id = idx
        self.args = args

class ParentCallNode(ExpressionNode):
    def __init__(self, obj, typex, idx, args):
        self.obj = obj
        self.type = typex
        self.id = idx
        self.args = args

################# Level 4 #################################################
class AtomicNode(ExpressionNode):
    def __init__(self, lex):
        self.lex = lex

class UnaryNode(ExpressionNode):
    def __init__(self, expr):
        self.expr = expr

class BinaryNode(ExpressionNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

################# Level 5 #################################################
class ConstantNumNode(AtomicNode):
    pass
class VariableNode(AtomicNode):
    pass
class InstantiateNode(AtomicNode):
    pass

class NotNode(UnaryNode):
    pass
class ComplementNode(UnaryNode):
    pass
class IsVoidNode(UnaryNode):
    pass

class EqualsGreatNode(BinaryNode):
    pass
class GreatNode(BinaryNode):
    pass
class EqualsNode(BinaryNode):
    pass
class PlusNode(BinaryNode):
    pass
class MinusNode(BinaryNode):
    pass
class StarNode(BinaryNode):
    pass
class DivNode(BinaryNode):
    pass