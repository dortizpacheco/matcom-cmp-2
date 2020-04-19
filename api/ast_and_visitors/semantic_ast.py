### Nivel 0 ######################
class Node:
    pass

### Nivel 1 ######################
class ProgramNode(Node):
    def __init__(self, statements):
        self.statements = statements
        
class StatementNode(Node):
    pass
        
class ExpressionNode(Node):
    pass

### Nivel 2 ######################
class VarDeclarationNode(StatementNode):
    def __init__(self, idx, expr):
        self.id = idx
        self.expr = expr

class FuncDeclarationNode(StatementNode):
    def __init__(self, idx, params, body):
        self.id = idx
        self.params = params
        self.body = body

class PrintNode(StatementNode):
    def __init__(self, expr):
        self.expr = expr

class AtomicNode(ExpressionNode):
    def __init__(self, lex):
        self.lex = lex

class BinaryNode(ExpressionNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

### Nivel 3 ############################
class ConstantNumNode(AtomicNode):
    pass

class VariableNode(AtomicNode):
    pass

class CallNode(AtomicNode):
    def __init__(self, idx, args):
        AtomicNode.__init__(self, idx)
        self.args = args

class PlusNode(BinaryNode):
    pass

class MinusNode(BinaryNode):
    pass

class StarNode(BinaryNode):
    pass

class DivNode(BinaryNode):
    passCallNode(ExpressionNode):
    def __init__(self, obj, idx, args):
        self.obj = obj
        self.id = idx
        self.args = args

################# Level 4 #################################################
class AtomicNode(ExpressionNode):
    def __init__(self, lex):
        self.lex = lex

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
class PlusNode(BinaryNode):
    pass
class MinusNode(BinaryNode):
    pass
class StarNode(BinaryNode):
    pass
class DivNode(BinaryNode):
    pass