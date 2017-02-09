import re
import ast
import types
import inspect
from textwrap import dedent
from collections import deque, defaultdict

from .features import *

FullPython = set([
    ImplicitCasts,
    Generators,
    DelVar,
    Closures,
    Classes,
    Decorators,
    VarArgs,
    KeywordArgs,
    Inheritance,
    MInheritance,
    ClassDecorators,
    Assertions,
    ChainComparison,
    Exceptions,
    Lambda,
    RelativeImports,
    ImportStar,
    HeteroList,
    Continue,
    MultipleReturn,
    DictComp,
    Ellipsi,
    TupleUnpacking,
    Exec,
    FancyIndexing,
    Globals,
    ContextManagers,
    GeneratorExp,
    Ternary,
    ListComp,
    SetComp,
    CustomIterators,
    Printing,
    Metaclasses
])

def _compile_lib_matcher(libs):
    matches = []
    for allowed in libs:
        matches.append(allowed.replace('.', '\\.')\
                              .replace('*', '.*$'))
    return r'|'.join(matches)

#------------------------------------------------------------------------
# AST Traversal
#------------------------------------------------------------------------

GLOBAL = 0

class PythonVisitor(ast.NodeVisitor):

    def __init__(self, features, libs):
        self.scope = deque([('global', 0)])
        self.features = features

        if libs:
            self.libs = _compile_lib_matcher(libs)
        else:
            self.libs = None

    def __call__(self, source):
        if isinstance(source, types.ModuleType):
            source = dedent(inspect.getsource(source))
        if isinstance(source, types.FunctionType):
            source = dedent(inspect.getsource(source))
        if isinstance(source, types.LambdaType):
            source = dedent(inspect.getsource(source))
        elif isinstance(source, str):
            source = source
        else:
            raise NotImplementedError

        self._source = source
        self._ast = ast.parse(source)
        self.visit(self._ast)

    def nolib(self, node, library):
        #print 'NO SUPPORT! %s' % library
        #print self._source.split('\n')[node.lineno-1]
        raise SystemExit()

    def action(self, node, feature):
        raise NotImplementedError

    # -------------------------------------------------

    def visit_comprehension(self, node):
        if node.ifs:
            ifs = list(map(self.visit, node.ifs))
        target = self.visit(node.target)
        iter = self.visit(node.iter)

    def visit_keyword(self, node):
        value = self.visit(node.value)

    def check_arguments(self, node):
        args = node.args

        ### Check for variadic arguments
        if VarArgs not in self.features:
            if args.vararg:
                self.action(node, VarArgs)

        ### Check for keyword arguments
        if KeywordArgs not in self.features:
            if args.kwarg:
                self.action(node, KeywordArgs)
            if args.defaults:
                self.action(node, KeywordArgs)

    # -------------------------------------------------

    def visit_Assert(self, node):
        ## Check for assertions
        if Assertions not in self.features:
            self.action(node, Assertions)

        test = self.visit(node.test)

    def visit_Assign(self, node):
        targets = node.targets

        ## Check for tuple unpacking
        if TupleUnpacking not in self.features:
            if len(node.targets) > 1:
                self.action(node, TupleUnpacking)

            if any(isinstance(x, ast.Tuple) for x in node.targets):
                self.action(node, TupleUnpacking)

        for target in targets:
            self.visit(target)
            self.visit(node.value)

            ## Check for metaclasses
            if Metaclasses not in self.features:
                if isinstance(target, ast.Name) and target.id == '__metaclass__':
                    self.action(node, Metaclasses)

    def visit_Attribute(self, node):
        value = self.visit(node.value)

    def visit_AugAssign(self, node):
        target = self.visit(node.target)
        value = self.visit(node.value)
        op = node.op.__class__

    def visit_BinOp(self, node):
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        op_str = node.op.__class__

        ## Check for implicit coercions between numeric types
        if ImplicitCasts not in self.features:
            if isinstance(node.left, ast.Num) and isinstance(node.right, ast.Num):
                a = node.left.n
                b = node.right.n
                if type(a) != type(b) and ImplicitCasts not in self.features:
                    self.action(node, ImplicitCasts)

    def visit_Break(self, node):
        pass

    def visit_BoolOp(self, node):
        operands = list(map(self.visit, node.values))
        operator = node.op.__class__

        ## Check for implicit coercions between numeric types
        if ImplicitCasts not in self.features:
            for operand in node.values:
                if isinstance(operand, ast.Num):
                    self.action(node, ImplicitCasts)

    # PY3
    def visit_Bytes(self, node):
        pass

    def visit_Call(self, node):
        name = self.visit(node.func)
        args = list(map(self.visit, node.args))
        keywords = list(map(self.visit, node.keywords))

        # Python 2.x - 3.4
        if hasattr(node,"starargs") and node.starargs:
            ## Check for variadic arguments
            starargs = self.visit(node.starargs)

            if VarArgs not in self.features:
                self.action(node, VarArgs)

        if (hasattr(node,'keywords') and node.keywords) or \
            (hasattr(node,'kwargs') and node.kwargs):
            ## Check for keyword arguments
            kwargs = list(map(self.visit, node.keywords))

            if KeywordArgs not in self.features:
                self.action(node, KeywordArgs)

        # Python 3.5+
        # TODO


    def visit_ClassDef(self, node):

        if Classes not in self.features:
            self.action(node, Classes)

        if node.bases:
            bases = list(map(self.visit, node.bases))

            ## Check for single inheritance
            if len(bases) >= 1 and Inheritance not in self.features:
                self.action(node, Inheritance)

            ## Check for multiple inheritance
            if len(bases) > 1 and MInheritance not in self.features:
                self.action(node, MInheritance)

        if node.decorator_list:
            decorators = list(map(self.visit, node.decorator_list))

            ## Check for class decorators
            if decorators and ClassDecorators not in self.features:
                self.action(node, ClassDecorators)


        self.scope.append(('class', node))
        body = list(map(self.visit, node.body))
        self.scope.pop()

    def visit_Compare(self, node):
        ## Check for chained comparisons
        if len(node.comparators) > 1 and ChainComparison not in self.features:
            self.action(node, ChainComparison)

        operands = list(map(self.visit, [node.left] + node.comparators))
        operators = [op.__class__ for op in node.ops]

    def visit_Continue(self, node):
        ## Check for continue
        if Continue not in self.features:
            self.action(node, Continue)

    def visit_Delete(self, node):
        target = list(map(self.visit, node.targets))
        if DelVar not in self.features:
            self.action(node, DelVar)

    def visit_Dict(self, node):
        keys = list(map(self.visit, node.keys))
        values = list(map(self.visit, node.values))

    def visit_DictComp(self, node):
        key = self.visit(node.key)
        value = self.visit(node.value)
        gens = list(map(self.visit, node.generators))

        ## Check for dictionary comprehensions
        if DictComp not in self.features:
            self.action(node, DictComp)

    def visit_Ellipsis(self, node):
        pass

    def visit_ExtSlice(self, node):
        list(map(self.visit, node.dims))

    def visit_ExceptHandler(self, node):

        if node.name:
            name = node.name.id
        #if node.type:
            #type = node.type.id
        body = list(map(self.visit, node.body))

        if Exceptions not in self.features:
            self.action(node, Exceptions)

    def visit_Exec(self, node):
        ## Check for dynamic exec
        if Exec not in self.features:
            self.action(node, Exec)

        body = self.visit(node.body)
        if node.globals:
            globals = self.visit(node.globals)
        if node.locals:
            locals = self.visit(node.locals)

    def visit_Expr(self, node):
        value = self.visit(node.value)

    def visit_For(self, node):
        target = self.visit(node.target)
        iter = self.visit(node.iter)
        body = list(map(self.visit, node.body))
        orelse = list(map(self.visit, node.orelse))

        ## Check for custom iterators
        if CustomIterators not in self.features:
            if not isinstance(node.iter, ast.Call):
                self.action(node, CustomIterators)
            elif isinstance(node.iter.func, ast.Name):
                if node.iter.func.id not in ['xrange', 'range']:
                    self.action(node, CustomIterators)
            else:
                self.action(node, CustomIterators)

        ## Check for tuple unpacking
        if TupleUnpacking not in self.features:
            if isinstance(node.target, ast.Tuple):
                self.action(node.target, TupleUnpacking)

    def visit_FunctionDef(self, node):
        self.check_arguments(node)

        if node.decorator_list:
            decorators = list(map(self.visit, node.decorator_list))

            ## Check for class decorators
            if decorators and Decorators not in self.features:
                self.action(node, Decorators)

        ## Check for closures
        scope_ty, scope = self.scope[-1]

        if scope_ty == 'function' and scope != GLOBAL:
            if Closures not in self.features:
                self.action(node, Closures)

        self.scope.append(('function', node))

        for defn in node.body:
            self.visit(defn)
        self.scope.pop()

    def visit_Global(self, node):
        ## Check for globals
        if Globals not in self.features:
            self.action(node, Globals)

    def visit_GeneratorExp(self, node):
        self.visit(node.elt)
        list(map(self.visit, node.generators))

        ## Check for dictionary comprehensions
        if GeneratorExp not in self.features:
            self.action(node, GeneratorExp)

    def visit_If(self, node):
        test = self.visit(node.test)
        body = list(map(self.visit, node.body))
        orelse = list(map(self.visit, node.orelse))

    def visit_IfExp(self, node):
        test = self.visit(node.test)
        body = self.visit(node.body)
        orelse = self.visit(node.orelse)

        if Ternary not in self.features:
            self.action(node, Ternary)

    def visit_Import(self, node):
        matcher = self.libs

        ## Check for unsupported libraries
        def check_import(name):
            if name.startswith('.') and RelativeImports not in self.features:
                self.action(node, RelativeImports)

            if not re.match(matcher, name):
                self.nolib(node, name)

        for package in node.names:
            if self.libs:
                check_import(package.name)

    def visit_ImportFrom(self, node):
        matcher = self.libs

        ## Check for unsupported libraries
        def check_import(name):

            if not re.match(matcher, name):
                self.nolib(node, name)

        for package in node.names:
            ## Check for "import *"
            if package.name == '*' and ImportStar not in self.features:
                self.action(node, ImportStar)

            if node.module == None:
                if RelativeImports not in self.features:
                    self.action(node, RelativeImports)

            if node.module and self.libs:
                munged = node.module + '.' + package.name
                check_import(munged)

    def visit_Index(self, node):
        self.visit(node.value)

    def visit_Lambda(self, node):
        ## Check for lambdas
        if Lambda not in self.features:
            self.action(node, Lambda)

        self.check_arguments(node)

        #args = self.visit(node.args)
        body = self.visit(node.body)

    def visit_List(self, node):
        elts = list(map(self.visit, node.elts))

        ## Check for hetereogenous lists
        if node.elts and not HeteroList in self.features:
            ty = type(node.elts[0])
            for el in node.elts[1:]:
                if type(el) != ty:
                    self.action(node, HeteroList)

    def visit_ListComp(self, node):
        elt = self.visit(node.elt)
        gens = list(map(self.visit, node.generators))

        ## Check for list comprehensions
        if ListComp not in self.features:
            self.action(node, ListComp)

    def visit_Name(self, node):
        pass

    def visit_Num(self, node):
        pass

    def visit_Module(self, node):
        body = list(map(self.visit, node.body))

    def visit_Pass(self, node):
        pass

    def visit_Print(self, node):
        ## Check for printing
        if Printing not in self.features:
            self.action(node, Printing)

        if node.dest:
            dest = self.visit(node.dest)

        values = list(map(self.visit, node.values))

    def visit_Raise(self, node):
        if node.type:
            self.visit(node.type)

        ## Check for exceptions
        if Exceptions not in self.features:
            self.action(node, Exceptions)

    def visit_Return(self, node):
        if node.value:
            self.visit(node.value)

        ## Check for multiple returns
        if isinstance(node.value, ast.Tuple) and MultipleReturn not in self.features:
            self.action(node, MultipleReturn)

    def visit_Set(self, node):
        elts = list(map(self.visit, node.elts))

    def visit_SetComp(self, node):
        elt = self.visit(node.elt)
        gens = list(map(self.visit, node.generators))

        ## Check for set comprehensions
        if SetComp not in self.features:
            self.action(node, SetComp)

    def visit_Slice(self, node):
        lower = node.lower
        if lower is not None:
            lower = self.visit(lower)

        upper = node.upper
        if upper is not None:
            upper = self.visit(upper)

        step = node.step
        if step is not None:
            step = self.visit(step)

    def visit_Str(self, node):
        pass

    def visit_Starred(self, node):
        self.visit(node.value)

    def visit_Subscript(self, node):
        value = self.visit(node.value)
        slice = self.visit(node.slice)

        ## Check for fancy indexing
        if isinstance(node.slice, ast.ExtSlice) and FancyIndexing not in self.features:
            self.action(node, FancyIndexing)

            ## Check for ellipsis
            if Ellipsi not in self.features:
                if any(type(a) == ast.Ellipsis for a in node.slice.dims):
                    self.action(node, Ellipsi)

        if isinstance(node.slice, ast.Ellipsis) and Ellipsi not in self.features:
            self.action(node, Ellipsi)

    def visit_TryExcept(self, node):
        body = list(map(self.visit, node.body))
        if node.handlers:
            handlers = list(map(self.visit, node.handlers))

        if node.orelse:
            orelse = list(map(self.visit, node.orelse))

        ## Check for exceptions
        if Exceptions not in self.features:
            self.action(node, Exceptions)

    def visit_TryFinally(self, node):
        body = list(map(self.visit, node.body))
        finalbody = list(map(self.visit, node.finalbody))

        ## Check for exceptions
        if Exceptions not in self.features:
            self.action(node, Exceptions)

    def visit_Tuple(self, node):
        return list(map(self.visit, node.elts))

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op = node.op.__class__

    def visit_While(self, node):
        test = self.visit(node.test)
        body = list(map(self.visit, node.body))
        if node.orelse:
            orelse = list(map(self.visit, node.orelse))

    def visit_With(self, node):
        ## Check for context managers
        if ContextManagers not in self.features:
            self.action(node, ContextManagers)

        exp = self.visit(node.context_expr)
        if node.optional_vars:
            var = node.optional_vars and self.visit(node.optional_vars)
        body = list(map(self.visit, node.body))

    def visit_Yield(self, node):
        ## Check for generators
        if Generators not in self.features:
            self.action(node, Generators)

        if node.value:
            value = self.visit(node.value)

    # PY3
    def visit_YieldFrom(self, node):
        if Generators not in self.features:
            self.action(node, Generators)

        if node.value:
            value = self.visit(node.value)

    def generic_visit(self, node):
        assert 0

#------------------------------------------------------------------------
# Validator
#------------------------------------------------------------------------

class FeatureNotSupported(SyntaxError): pass

class Validator(PythonVisitor):
    """ Check if the given source conforms to the feature set or
    raise an Exception. """

    def action(self, node, feature):
        line = self._source.splitlines()[node.lineno-1]
        lineno = node.lineno
        offset = node.col_offset
        raise FeatureNotSupported(feature, ('<stdin>', lineno, offset + 1, line))

class Checker(PythonVisitor):
    """ Aggregate sites for features that don't conform to the
    given feature set """

    def __init__(self, features, libraries):
        super(Checker, self).__init__(features, libraries)
        self.detected = None

    def action(self, node, feature):
        self.detected[feature].append(node.lineno)

    def __call__(self, source):
        self.detected = defaultdict(list)
        super(Checker, self).__call__(source)
        return dict(self.detected)

class Detect(PythonVisitor):
    """ Aggregate sites for conform to the given feature set """

    def __init__(self):
        super(Detect, self).__init__(set(), [])
        self.detected = None

    def action(self, node, feature):
        self.detected[feature].append(node.lineno)

    def __call__(self, source):
        self.detected = defaultdict(list)
        super(Detect, self).__call__(source)
        return dict(self.detected)

def detect(source):
    d = Detect()
    return d(source)

def checker(source, features=None, libraries=None):
    d = Checker(features or set(), libraries or list())
    return d(source)

def validator(source, features=None, libraries=None):
    d = Validator(features or set(), libraries or list())
    return d(source)

fd = detect
