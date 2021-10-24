from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModule, PythonModuleCst
from snakepack.config import GlobalOptions
from snakepack.transformers.python.remove_pass import RemovePassTransformer
from tests.integration.transformers._base import TransformerIntegrationTestBase


class RemovePassTransformerIntegrationTest(TransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    if True: pass
                    else: pass
                    while True: pass
                    for a in b: pass
                    def c(): pass
                    class D: pass
                    try: pass
                    except: pass
                    else: pass
                    finally: pass
                    
                    if True: 1; pass
                    else: 1; pass
                    while True: 1; pass
                    for a in b: 1; pass
                    def c(): 1; pass
                    class D: 1; pass
                    try: 1; pass
                    except: 1; pass
                    else: 1; pass
                    finally: 1; pass
                    
                    if True: pass; 1
                    else: pass; 1
                    while True: pass; 1
                    for a in b: pass; 1
                    def c(): pass; 1
                    class D: pass; 1
                    try: pass; 1
                    except: pass; 1
                    else: pass; 1
                    finally: pass; 1
                    
                    try:
                        x=5
                        pass
                        y=6
                    except:
                        pass
                    
                    for a in b:
                        class Foo: pass
                    
                    while True:
                        print('ok'); pass
                    """
                )
            )
        )

        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    if True: 0
                    else: 0
                    while True: 0
                    for a in b: 0
                    def c(): 0
                    class D: 0
                    try: 0
                    except: 0
                    else: 0
                    finally: 0
                    
                    if True: 1; 
                    else: 1; 
                    while True: 1; 
                    for a in b: 1; 
                    def c(): 1; 
                    class D: 1; 
                    try: 1; 
                    except: 1; 
                    else: 1; 
                    finally: 1; 
                    
                    if True: 1
                    else: 1
                    while True: 1
                    for a in b: 1
                    def c(): 1
                    class D: 1
                    try: 1
                    except: 1
                    else: 1
                    finally: 1
                    
                    try:
                        x=5
                        y=6
                    except:
                        0
                    
                    for a in b:
                        class Foo: 0
                    
                    while True:
                        print('ok'); 
                    """
                )
            )
        )
        global_options = GlobalOptions()
        transformer = RemovePassTransformer(global_options=global_options)

        self._test_transformation(transformer=transformer, input=input_content, expected_output=expected_output_content)