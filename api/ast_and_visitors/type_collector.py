from cp14._import import *

class TypeCollector(object):
    def __init__(self, errors=[]):
        self.context = None
        self.errors = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node):
        self.context = Context()
        self.context.types = TypeBuilIn.all()
        for class_declaration in node.declarations:
            self.visit(class_declaration)
        return self.context

    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        self.context.create_type(node.id)
        
    
class TypeBuilIn:

    @staticmethod
    def all():
        return {
            "int" : IntType(),
            "void": VoidType() 
        }