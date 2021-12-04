from typing import Optional, Union, Dict, Tuple, Mapping, Type

from boltons.iterutils import first, flatten
from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, ClassDef, Name, CSTNode, Expr, BaseString, SimpleString, BaseExpression, Module, Assign, \
    AssignTarget, SimpleWhitespace

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.literals import LiteralDuplicationAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets import AssetGroup
from snakepack.assets.python import PythonModule, Python, PythonModuleCst
from snakepack.transformers.python._base import PythonModuleTransformer
from snakepack.transformers.python._renaming import NameRegistry


class HoistLiteralsTransformer(PythonModuleTransformer):
    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._name_registry = NameRegistry()
            self._hoisted_literals: Dict[str, Tuple[str, BaseExpression]] = {}

        def leave_SimpleString(self, original_node: SimpleString, updated_node: SimpleString) -> BaseExpression:
            num_occurrences = self._analyses[LiteralDuplicationAnalyzer].get_num_occurrences(self._subject, original_node)

            if num_occurrences < 2:
                # don't hoist if only used once
                return updated_node

            # check if assignment exists for this value
            scope = self._analyses[ScopeAnalyzer][self._subject][original_node]
            assignments = self._analyses[LiteralDuplicationAnalyzer].get_preceding_assignments(self._subject, original_node)

            if assignments is not None and len(assignments) > 0:
                # use existing assigned identifier
                use_existing_assignment = True
                new_identifier = first(assignments)
            else:
                use_existing_assignment = False

                # calculate size impact of hoisting
                if updated_node.value in self._hoisted_literals:
                    # we already marked this literal as a candidate for hoisting, reuse that identifier
                    new_identifier = self._hoisted_literals[updated_node.value][0]
                else:
                    # first time calculating hoisting impact for this literal, generate new identifier
                    new_identifier = self._name_registry.generate_name_for_scope(scope=scope)

                non_hoisted_char_count = len(updated_node.value) * num_occurrences
                assign_char_count = len(updated_node.value) + 1 + len(new_identifier)
                hoisted_char_count = assign_char_count + (2 * len(new_identifier))

                if non_hoisted_char_count <= hoisted_char_count:
                    # don't hoist because no size reduction
                    self._name_registry.reset(scope=scope)
                    return updated_node

                if updated_node.value not in self._hoisted_literals:
                    # we'll be using the generated identifier for hoisting
                    self._name_registry.register_name_for_scope(scope=scope, name=new_identifier)

            if not use_existing_assignment:
                # mark the literal for hoisting with a new variable assignment
                self._hoisted_literals[updated_node.value] = new_identifier, updated_node
            else:
                # reuse existing assignment
                if original_node in map(lambda x: x.value, flatten(map(lambda x: x[1], assignments.items()))):
                    # do not replace literal with a reference in the assignment itself
                    return updated_node

            # replace the literal with reference to a variable
            return Name(value=new_identifier)

        def leave_Module(self, original_node: Module, updated_node: Module) -> Module:
            updated_body = list(updated_node.body)
            hoist_assignments = []

            for new_identifier, literal_node in self._hoisted_literals.values():
                # assign literal to variable
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

            if len(hoist_assignments) == 0:
                # nothing hoisted
                return updated_node

            updated_body.insert(0, SimpleStatementLine(body=hoist_assignments))
            return updated_node.with_changes(body=updated_body)

    __config_name__ = 'hoist_literals'

