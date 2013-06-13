SmallPy Language Specification
------------------------------

Motivation:

- Establish a "Numeric Recipies in C" subset of Python. Just
  unambiguously make numeric loops fast, do this well because it
  generates revenue for Continuum. Then keep the "clever path" as
  an ongoing project into how to type larger sets of Python.

- Allow perfect reasoning about performance by demarcating a
  subset of Python that either lowers into LLVM or fails to
  compile.
  
- If code compiles it is guaranteed to be faster than the
  equivalent CPython.

- Improve the overall user experience of error reporting so that
  the end-user knows how to change their code to match the
  subset.

- Explicit is better than implicit. If the end user wants to go
  through the Object Layer make them say so.

Types
-----

- int
- float
- bool
- string
- unicode
- complex
- list
- tuple
- NoneType
- FunctionType

Unsupported Types:

- object
- dict
- set
- long
- frozenset
- buffer
- bytearray
- bytes
- basestring
- memoryview

Values
------

Tuple unpacking is not supported.

Assignment to tuples is syntactic sugar for multiple assignment
only when r-values are literals.

Supported:

```
a, b = 1, True
```

Not Supported:

```
a, b = f()
```

Control Flow
------------

Supported:

- If
- If/Else
- If/ElseIf/Else
- For
- While

Not Supported:

- Generators
- Exceptions
- Try
- Try/Finally
- Try/Except
- Try/Except/Finally
- While/Else
- For/Else

Data Model
----------

- Lists are stricly homogeneus containers of data. The
  storage is compiler specific.
- Tuples are heteroegneous immutable types. The storage is
  compiler specific.
- Strings are variable immutable arrays of ascii characters. The
  storage is compiler specific.
- Unicode strings are immutable arrays of UTF-8 characters. The
  storage is compiler specific.

```
list :: a -> [a]
```

Introspection
-------------

Runtime introspection with ``type``, ``isinstance``,
``issubclass``, ``id``, ``globals``, ``locals``, ``dir``,
``callable``, ``getattr``, ``hash``, ``hasattr``, ``super``,
``vars`` is not supported.

The ``intern`` function is not supported.

Length
------

Implementation is compiler specific.

```python
len :: [a] -> int
```

Destruction
-----------

Variable and element destruction is not supported. The ``del``
operator is not part of the syntax and ``delattr` is not
supported.

Metaprogramming
---------------

``compile``, ``eval`` and ``exec``, ``execfile`` are not supported

Pass
----

Pass is a syntactic construct that translates into a compiler
specific noop.

System IO
---------

``file``, ``open`` and ``quit``, ``raw_input``, ``reload``,
``help`` and ``input``.

``print`` is optionally supported. The implementation is specific
to the compiler. For compilers that do not choose to implement
print it should translate to noop.

The ``repr`` function is not supported.

Formatting
----------

Printf style formatting is not supported. The ``Mod`` operator
exclusively maps to numeric modulus.

Iterators
---------

Generators are not supported.

Range iterators are syntactic sugar for looping constructs. Custom
iterators are not supported. The ``iter`` and ``next`` functions
are not supported.

```
for i in xrange(start, stop, step
    foo()
```

Is lowered into some equivalent low-level looping construct that
roughly corresponds to the following C code:

```
for (i = start; i < stop; i += step) {
    foo();
}
```

``xrange`` and `range`` are lowered into the same constructs.

``enumerate`` is not supported

Comprehensions
--------------

TODO

Builtins
--------

* abs            -  Supported 
* all            -  Supported 
* any            -  Supported 
* apply          -  Not Supported   
* basestring     -  Not Supported        
* bin            -  Not Supported 
* bool           -  Supported  
* buffer         -  Not Supported    
* bytearray      -  Not Supported       
* bytes          -  Not Supported   
* callable       -  Not Supported      
* chr            -  Not Supported 
* classmethod    -  Not Supported         
* cmp            -  Supported 
* coerce         -  Not Supported    
* compile        -  Not Supported     
* complex        -  Supported     
* copyright      -  Not Supported       
* credits        -  Not Supported     
* delattr        -  Not Supported     
* dict           -  Not Supported  
* dir            -  Not Supported 
* divmod         -  Supported    
* enumerate      -  Not Supported       
* eval           -  Not Supported  
* execfile       -  Not Supported      
* exit           -  Not Supported  
* file           -  Not Supported  
* filter         -  Supported    
* float          -  Supported   
* format         -  Not Supported    
* frozenset      -  Not Supported       
* getattr        -  Not Supported     
* globals        -  Not Supported     
* hasattr        -  Not Supported     
* hash           -  Not Supported  
* help           -  Not Supported  
* hex            -  Not Supported 
* id             -  Not Supported
* input          -  Not Supported   
* int            -  Supported 
* intern         -  Not Supported    
* isinstance     -  Not Supported        
* issubclass     -  Not Supported        
* iter           -  Not Supported  
* len            -  Supported 
* license        -  Not Supported     
* list           -  Not Supported  
* locals         -  Not Supported    
* long           -  Not Supported  
* map            -  Supported 
* max            -  Supported 
* memoryview     -  Not Supported        
* min            -  Supported 
* next           -  Not Supported  
* object         -  Not Supported    
* oct            -  Not Supported 
* open           -  Not Supported  
* ord            -  Not Supported 
* pow            -  Supported 
* print          -  Not Supported   
* property       -  Not Supported      
* quit           -  Not Supported  
* range          -  Supported   
* raw_input      -  Not Supported       
* reduce         -  Supported    
* reload         -  Not Supported    
* repr           -  Not Supported  
* reversed       -  Not Supported      
* round          -  Supported   
* set            -  Not Supported 
* setattr        -  Not Supported     
* slice          -  Not Supported   
* sorted         -  Supported    
* staticmethod   -  Not Supported          
* str            -  Supported 
* sum            -  Supported 
* super          -  Not Supported   
* tuple          -  Not Supported   
* type           -  Not Supported  
* unichr         -  Not Supported    
* unicode        -  Supported     
* vars           -  Not Supported  
* xrange         -  Supported    
* zip            -  Supported 


Filter
------

```python
filter :: (a -> bool) -> [a] -> [a]
def filter(p, xs):
    return [x for x in xs if p(x)]
```

All
---


```python
all :: (a -> bool) -> [a] -> bool
def all(p, xs):
    for i in xs:
        if not p(i):
            return False
    return True
```

Any
---

```python
any :: (a -> bool) -> [a] -> bool
def any(p, xs):
    for i in xs:
        if not p(i):
            return True
    return False
```

Map
---

```python
map :: (a -> b) -> [a] -> [b]
def map(f, xs):
    return [f(x) for x in xs]
```

Reduce
------

```python
reduce :: (a -> b -> a) -> a -> [b] -> a
def reduce(p, xs, x0):
    acc = x0
    for x in xs:
        acc = f(acc)
    return acc
```

Max
---

```python

max :: [a] -> a
def max(xs):
    assert len(xs) > 0
    x0 = xs[0]
    for x in xs:
        if x > x0:
            x0 = x
    return x0
```

Min
---

```python

min :: [a] -> a
def min(xs):
    assert len(xs) > 0
    x0 = xs[0]
    for x in xs:
        if x < x0:
            x0 = x
    return x0
```

Zip
---

```python
min :: [a] -> [b] -> [(a, b)] 
def min(xs, ys):
    out = []
    for i in min(len(xs), len(ys)):
        out.append((xs[i], ys[i]))
    return out
```

Reverse
-------

```
reverse :: [a] -> [a]
def reverse(xs):
    out = []
    for i in len(xs):
        out.append(xs[len(xs)-i])
    return out
```

Sorted
------

Sorted sorts the underlying list data structure. The
implementation is compiler specific.

```python
sorted :: [a] -> [a]
```

Slice
-----

Named slicing is not supported. Slice types are not supported.
Slicing as an indexing operation is supported.

```
a = slice(0, 1, 2)
```

Classes
-------

Classes are not supported. The corresponding descriptor methods
are not implemented.

- property
- classmethod
- staticmethod

Casts
-----

```
int :: a -> int
bool :: a -> bool
complex :: a -> bool
```

The coerce function is not supported.

The ``str``, ``list`` and ``tuple`` casts are not supported.

Characters
----------

The ``chr``, ``ord`` and ``unichr``, ``hex``, ``bin``, ``oct``
functions are not supported.

Closures
--------

Nested functions and closures are not supported.

Globals
-------

Global variables are not supported.

Arguments
---------

Variadic and keyword arguments are not supported.

Assertions
----------

Assertions are not supported.

Syntax
------

Language Features

```

module SmallPython
{
	mod = Module(stmt* body)
	    | Expression(expr body)

	stmt = FunctionDef(identifier name, arguments args, 
                           stmt* body, expr? returns)
	      | Return(expr? value)

	      | Assign(expr* targets, expr value)
	      | AugAssign(expr target, operator op, expr value)

	      | For(expr target, expr iter, stmt* body, stmt* orelse)
	      | While(expr test, stmt* body, stmt* orelse)
	      | If(expr test, stmt* body, stmt* orelse)

	      | Expr(expr value)
	      | Pass | Break | Continue

	      attributes (int lineno, int col_offset)

	expr = BoolOp(boolop op, expr* values)
	     | BinOp(expr left, operator op, expr right)
	     | UnaryOp(unaryop op, expr operand)
	     | IfExp(expr test, expr body, expr orelse)
	     | ListComp(expr elt, comprehension* generators)
	     | Compare(expr left, cmpop* ops, expr* comparators)
	     | Call(expr func, expr* args, keyword* keywords,
			 expr? starargs, expr? kwargs)
	     | Num(object n) -- a number as a PyObject.
	     | Str(string s) -- need to specify raw, unicode, etc?
	     | Bytes(string s)

	     | Attribute(expr value, identifier attr, expr_context ctx)
	     | Subscript(expr value, slice slice, expr_context ctx)
	     | Name(identifier id, expr_context ctx)
	     | List(expr* elts, expr_context ctx) 
	     | Tuple(expr* elts, expr_context ctx)

	      attributes (int lineno, int col_offset)

	expr_context = Load | Store | AugLoad | AugStore | Param

	slice = Slice(expr? lower, expr? upper, expr? step) 
	      | ExtSlice(slice* dims) 
	      | Index(expr value) 

	boolop = And | Or 

	operator = Add | Sub | Mult | Div | Mod | Pow | LShift 
                 | RShift | BitOr | BitXor | BitAnd | FloorDiv

	unaryop = Invert | Not | UAdd | USub

	cmpop = Eq | NotEq | Lt | LtE | Gt | GtE

	comprehension = (expr target, expr iter, expr* ifs)

	arguments = (arg* args, identifier? vararg, expr? varargannotation,
                     arg* kwonlyargs, identifier? kwarg,
                     expr? kwargannotation, expr* defaults,
                     expr* kw_defaults)
	arg = (identifier arg, expr? annotation)

        keyword = (identifier arg, expr value)
        alias = (identifier name, identifier? asname)
}

```


Operators
---------

- And      
- Or       
- Add      
- Sub      
- Mult     
- Div      
- Mod      
- Pow      
- LShift   
- RShift   
- BitOr    
- BitXor   
- BitAnd   
- FloorDiv 
- Invert   
- Not      
- UAdd     
- USub     
- Eq       
- NotEq    
- Lt       
- LtE      
- Gt       
- GtE      

Comparison operator chaining is supported.

Smallpy explictly does not support the following operators.

- Is
- IsNot
- In
- NotIn


Math Functions
--------------

abs
cmp
divmod
pow
round

sorted

Floating Point Math
-------------------

```
acos
acosh
asin
asinh
atan
atan2
atanh
ceil
copysign
cos
cosh
degrees
e
erf
erfc
exp
expm1
fabs
factorial
floor
fmod
frexp
fsum
gamma
hypot
isinf
isnan
ldexp
lgamma
log
log10
log1p
modf
pi
pow
radians
sin
sinh
sqrt
tan
tanh
trunc
```

Complex Math

```
acos
acosh
asin
asinh
atan
atanh
cos
cosh
exp
isinf
isnan
log
log10
phase
polar
rect
sin
sinh
sqrt
tan
tanh
```
