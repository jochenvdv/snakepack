from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModule, PythonModuleCst
from snakepack.config import GlobalOptions
from snakepack.transformers.python.remove_whitespace import RemoveWhitespaceTransformer
from tests.integration.transformers._base import TransformerIntegrationTestBase


class RemoveWhitespaceTransformerIntegrationTest(TransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    x = 5
                    foo(x)
                    del  x
                    assert  x
                    global  x
                    import  x
                    from  x  import  a  
                    import  x  as  y 
                    from  x  import  y  as  z 
                    nonlocal  b
                    raise  
                    raise  a  
                    return  
                    return  a 
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
                    """
                )
            )
        )
        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    x=5;foo(x);del x;assert x;global x;import x;from x import a;import x as y;from x import y as z;nonlocal b;raise;raise a;return;return a;x:Foo;a:int=7;b=8;foo(a,foo(8),x=x)
                    if True:
                     a();b()#  this is a comment  
                     x=5
                    for a in b:
                     pass
                    def Foo(a:int,b:int=0 )->bool:
                     pass
                    try:
                     pass
                    except:
                     pass
                    try:
                     pass
                    except Exception:
                     pass
                    try:
                     pass
                    except Exception as e:
                     pass
                    while True:
                     pass
                    with foo():
                     pass
                    with foo() as d:
                     pass
                    @decorator
                    def foo():
                     pass
                    if False:
                     pass
                    else:
                     pass
                    try:
                     pass
                    finally:
                     pass
                    """
                ).strip()
            )
        )
        global_options = GlobalOptions()
        transformer = RemoveWhitespaceTransformer(global_options=global_options)

        self._test_transformation(transformer=transformer, input=input_content, expected_output=expected_output_content)