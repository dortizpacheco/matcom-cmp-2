from cp14._import import *

class TypeBuilder:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.errors = errors

    def _find_type(self,ttype):
        try:
            return self.context.get_type(ttype)
        except SemanticError as error:
            self.errors.append(error.text)
            return ErrorType()

    @visitor.on('node')
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node):
        for class_declaration in node.declarations:
            self.visit(class_declaration)
            

    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        self.current_type = self._find_type(node.id)
        if not node.parent is None: self.current_type.set_parent(self._find_type(node.parent)) 
        for attr in node.features:
            self.visit(attr)
    

    @visitor.when(AttrDeclarationNode)
    def visit(self, node):
        try:
            self.current_type.define_attribute(node.id,self._find_type(node.type))
        except SemanticError as error:
            self.errors.append(error.text)

    @visitor.when(FuncDeclarationNode)
    def visit(self, node):
        params_type = []
        for name,ptype in node.params:
            params_type.append(self._find_type(ptype))
        try:
            self.current_type.define_method(node.id,node.params,params_type,self._find_type(node.type))
        except SemanticError as error:
            self.errors.append(error.text)