from typing import Optional, Union, Dict, Tuple, Mapping, Type

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, ClassDef, Name, CSTNode, Expr, BaseString, SimpleString, BaseExpression, Module, Assign, \
    AssignTarget, SimpleWhitespace

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.literals import LiteralDuplicationAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets import AssetGroup
from snakepack.assets.python import PythonModule, Python, PythonModuleCst
from snakepack.transformers.python._base import PythonModuleTransformer


class HoistLiteralsTransformer(PythonModuleTransformer):
    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._hoisted_literals: Dict[str, Tuple[str, BaseExpression]] = {}
            self._existing_assignments: Dict[str, str]

        def leave_SimpleString(self, original_node: SimpleString, updated_node: SimpleString) -> BaseExpression:
            num_occurrences = self._analyses[LiteralDuplicationAnalyzer].get_num_occurrences(self._subject, original_node)

            if num_occurrences < 2:
                # don't hoist if only used once
                return updated_node

            # check if assignment exists for this value

            # calculate size impact of hoisting
            new_identifier = 'a'
            non_hoisted_char_count = len(updated_node.value) * num_occurrences
            assign_char_count = len(updated_node.value) + 1 + len(new_identifier)
            hoisted_char_count = assign_char_count + (2 * len(new_identifier))

            if non_hoisted_char_count <= hoisted_char_count:
                # don't hoist because no size reduction
                return updated_node

            # replace literal with variable access
            self._hoisted_literals[updated_node.value] = new_identifier, updated_node
            return Name(value=new_identifier)

        def leave_Module(self, original_node: Module, updated_node: Module) -> Module:
            updated_body = list(updated_node.body)
            hoist_assignments = []

            for new_identifier, literal_node in self._hoisted_literals.values():
                hoist_assignments.append(Assign(
                    targets=[
                        AssignTarget(
                            target=Name(
                                value=new_identifier
                            ),
                            whitespace_before_equal=SimpleWhitespace(
                                value=''
                            ),
                            whitespace_after_equal=SimpleWhitespace(
                                value=''
                            )
                        )
                    ],
                    value=literal_node,
                    semicolon=MaybeSentinel.DEFAULT
                ))

            updated_body.insert(0, SimpleStatementLine(body=hoist_assignments))

            return updated_node.with_changes(body=updated_body)

    __config_name__ = 'hoist_literals'

