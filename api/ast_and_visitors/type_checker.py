from ._import import *

class TypeChecker:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.current_method = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope=None):
        scope = Scope()
        for declaration in node.declarations:
            self.visit(declaration, scope.create_child())
        return scope

    @visitor.when(ClassDeclarationNode)
    def visit(self, node, scope):
        pass
        
    @visitor.when(AttrDeclarationNode)
    def visit(self, node, scope):
        pass

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope):
        pass
    
    @visitor.when(VarDeclarationNode)
    def visit(self, node, scope):
        pass
            
    @visitor.when(AssignNode)
    def visit(self, node, scope):
        pass
    
    @visitor.when(CallNode)
    def visit(self, node, scope):
        pass
    
    @visitor.when(BinaryNode)
    def visit(self, node, scope):
        pass
    
    @visitor.when(ConstantNumNode)
    def visit(self, node, scope):
        pass

    @visitor.when(VariableNode)
    def visit(self, node, scope):
        pass

    @visitor.when(InstantiateNode)
    def visit(self, node, scope):
        pass

