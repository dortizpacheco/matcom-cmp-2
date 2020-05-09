import cmp.visitor as visitor
from .semantic_ast import BinaryNode, UnaryNode, AtomicNode

from .import ProgramNode
from .import ClassDeclarationNode, FuncDeclarationNode, AttrDeclarationNode
from .import LetNode, IfNode, WhileNode, BlocksNode, CaseNode, AssignNode
from .import VarDeclarationNode, SingleCaseNode
from .import CallNode, InstanceCallNode, ParentCallNode
from .import InstantiateNode,ConstantNumNode,VariableNode
from .import NotNode, ComplementNode, IsVoidNode
from .import EqualsNode, GreatNode, EqualsGreatNode
from .import PlusNode, MinusNode, StarNode, DivNode

class FormatVisitor(object):
    @visitor.on('node')
    def visit(self, node, tabs = 0):
        return f'{node}\n'
    
    @visitor.when(ProgramNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ProgramNode [<class> ... <class>]'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.declarations)
        return f'{ans}\n{statements}'

###################################  Class Body  #################################################################
    @visitor.when(ClassDeclarationNode)
    def visit(self, node, tabs=0):
        parent = '' if node.parent is None else f": {node.parent}"
        ans = '\t' * tabs + f'\\__ClassDeclarationNode: class {node.id} {parent} {{ <feature> ... <feature> }}'
        features = '\n'.join(self.visit(child, tabs + 1) for child in node.features)
        return f'{ans}\n{features}'
    
    @visitor.when(AttrDeclarationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__AttrDeclarationNode: {node.id} : {node.type}'
        return f'{ans}'
    
    @visitor.when(FuncDeclarationNode)
    def visit(self, node, tabs=0):
        params = ', '.join(':'.join(param) for param in node.params)
        ans = '\t' * tabs + f'\\__FuncDeclarationNode: {node.id}({params}) : {node.type} -> <body>'
        body = '\n'.join(self.visit(child, tabs + 1) for child in node.body)
        return f'{ans}\n{body}'

###################################  "Statement"  #################################################################
    @visitor.when(LetNode)
    def visit(self, node, tabs = 0):
        ans = '\t' * tabs + f'\\__LetNode:'
        var_list = '\n'.join(self.visit(var, tabs + 1) for var in node.list)
        expr = '\t' * tabs + f'\\__In:\n' + self.visit(node.expr, tabs + 1)
        return f'{ans}\n{var_list}\n{expr}'
    
    @visitor.when(VarDeclarationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__VarDeclarationNode: let {node.id} : {node.type} [<- expr]'
        expr = '' if node.parent is None else  self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'
    
    @visitor.when(IfNode)
    def visit(self, node, tabs = 0):
        _if = '\t' * tabs + f'\\__IfNode:'
        cond = self.visit(node.condiction, tabs + 1)
        then = '\t' * tabs + f'\\__Then:'
        then_expr = self.visit(node.then, tabs + 1)
        _else = '\t' * tabs + f'\\__Else:'
        else_expr = self.visit(node._else, tabs + 1)
        return f'{_if}\n{cond}\n{then}\n{then_expr}\n{_else}\n{else_expr}'

    @visitor.when(WhileNode)
    def visit(self, node, tabs = 0):
        _while = '\t' * tabs + f'\\__WhileNode:'
        cond = self.visit(node.condiction, tabs + 1)
        loop = '\t' * tabs + f'\\__Loop:'
        body = self.visit(node.body, tabs + 1)
        pool = '\t' * tabs + f'\\__Pool:'
        return f'{_while}\n{cond}\n{loop}\n{body}\n{pool}'

    @visitor.when(BlocksNode)
    def visit(self, node, tabs = 0):
        block = '\t' * tabs + f'\\__BlocksNode:'
        _list = '\n'.join(self.visit(expr, tabs + 1 ) for expr in node._list)
        return f'{block}\n{_list}'

    @visitor.when(CaseNode)
    def visit(self, node, tabs = 0):
        case = '\t' * tabs + f'\\__CaseNode:'
        expr = self.visit(node.expr, tabs + 1)
        _list = '\t' * tabs + f'\\__OptionsList:'
        list_case = '\n'.join(self.visit(case, tabs + 1) for case in node.case_list)
        return f'{case}\n{expr}\n{_list}\n{list_case}'

    @visitor.when(SingleCaseNode)
    def visit(self, node, tabs = 0):
        case = '\t' * tabs + f'\\__SingleCaseNode: {node.id} : {node.type} => expr'
        expr = self.visit(node.expr, tabs + 1)
        return f'{case}\n{expr}'

    @visitor.when(AssignNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__AssignNode: {node.id} = <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

###################################  "Call"  #################################################################
    @visitor.when(CallNode)
    def visit(self, node, tabs = 0):
        ans = '\t' * tabs + f'\\__CallNode: {node.id} \\__Params:'
        params = '\n'.join( self.visit(param, tabs + 1) for param in node.args)
        return f'{ans}\n{params}'

    @visitor.when(InstanceCallNode)
    def visit(self, node, tabs = 0):
        ans = '\t' * tabs + f'\\__InstanceCallNode: {node.id} \\__Object:'
        obj = self.visit(node.obj, tabs + 1)
        param = '\t' * tabs + f'\\__Params:'
        params = '\n'.join( self.visit(param, tabs + 1) for param in node.args)
        return f'{ans}\n{obj}\n{param}\n{params}'

    @visitor.when(ParentCallNode)
    def visit(self, node, tabs = 0):
        ans = '\t' * tabs + f'\\__InstanceCallNode: {node.type} @ {node.id} \\__Object:'
        obj = self.visit(node.obj, tabs + 1)
        param = '\t' * tabs + f'\\__Params:'
        params = '\n'.join( self.visit(param, tabs + 1) for param in node.args)
        return f'{ans}\n{obj}\n{param}\n{params}'
    
###################################  "Last Expression"  #################################################################    
    @visitor.when(BinaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(UnaryNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.expr}'
    
    @visitor.when(AtomicNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.lex}'

    @visitor.when(InstantiateNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ InstantiateNode: new {node.lex}()'