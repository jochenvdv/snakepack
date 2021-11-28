from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_whitespace import RemoveWhitespaceTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveWhitespaceTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    x = 5
                    foo(x)
                    del  x
                    assert  x
                    global  u
                    import  x
                    from  x  import  a  
                    import  x  as  y 
                    from  x  import  y  as  z
                     
                    def bar():
                        b = True
                        def _():
                            nonlocal  b
                            
                    raise  
                    raise  a  
                    def xxx(): return  
                    def yyy(a): return  a 
                    x : Foo 
                    a : int = 7 ; b = 8  
                    foo ( a, foo ( 8 ) , x = x  )

                    
                    if  True :
                        a()
                        
                        b() #  this is a comment  
                        x=5
                    
                    for  a  in  b  :
                        pass
                    
                    def  Foo ( a : int, b : int = 0 )  ->  bool:
                        pass
                        
                    try :
                        pass
                    except :
                        pass
                    try:
                        pass
                    except  Exception  :
                        pass
                    try:
                        pass
                    except  Exception  as  e  :
                        pass
                    
                    while  True  :
                        pass
                        
                    with  foo () :
                        pass
                        
                    with  foo()  as  d  :
                        pass
                    
                    @  decorator    
                    def foo():
                        pass
                        
                    if False:
                        pass
                    else  :
                        pass
                        
                    try:
                        pass
                    finally  :
                        pass
                        
                    async  def foo(a, b):
                        async  for a in b: pass
                        await  foo()
                        yield  
                        yield  x  
                    def baz(b):
                        yield  from  b()
                    x  if  True  else  y 
                    lambda  :  None
                    lambda  a, * b, c : None
                    "foo"  "foo"
                    f"a{ b }c"
                    [ *  foo ]
                    { 'foo' : True , **  foo }
                    ( foo )
                    a [ 'foo' ]
                    [ a  for  a  in  b  if  c  is  True  and  False  or  True  ]
                    not  foo 
                    -  1 
                    1  +  1
                    1  ==  1
                    1  not  in  []
                    foo  is  not  True
                    
                    from a import (
                        b,
                        c
                    ) 
                    
                    from a import  (
                        b, # this is a comment
                        
                        # this as well
                        
                        
                        c,
                        d
                    )
                    """
                )
            )
        )
        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    x=5;foo(x);del x;assert x;global u;import x;from x import a;import x as y;from x import y as z
                    def bar():
                     b=True
                     def _():nonlocal b
                    raise;raise a
                    def xxx():return
                    def yyy(a):return a
                    x:Foo;a:int=7;b=8;foo(a,foo(8),x=x)
                    if True:
                     a();b()#this is a comment
                     x=5
                    for a in b:pass
                    def Foo(a:int,b:int=0)->bool:pass
                    try:pass
                    except:pass
                    try:pass
                    except Exception:pass
                    try:pass
                    except Exception as e:pass
                    while True:pass
                    with foo():pass
                    with foo() as d:pass
                    @decorator
                    def foo():pass
                    if False:pass
                    else:pass
                    try:pass
                    finally:pass
                    async def foo(a,b):
                     async for a in b:pass
                     await foo();yield;yield x
                    def baz(b):yield from b()
                    x if True else y;lambda:None;lambda a,*b,c:None;"foo""foo";f"a{b}c";[*foo];{'foo':True,**foo};(foo);a['foo'];[a for a in b if c is True and False or True];not foo;-1;1+1;1==1;1 not in [];foo is not True;from a import (b,c);from a import (b,#this is a comment
                    #this as well
                    c,d)
                    """
                ).strip()
            )
        )
        global_options = GlobalOptions()
        transformer = RemoveWhitespaceTransformer(global_options=global_options)

        self._test_transformation(transformer=transformer, input=input_content, expected_output=expected_output_content)