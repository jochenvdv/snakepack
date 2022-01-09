from typing import Optional, Union, Dict, Tuple, Mapping, Type

from boltons.iterutils import first, flatten
from libcst import IndentedBlock, CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, ClassDef, Name, CSTNode, Expr, BaseString, SimpleString, BaseExpression, Module, Assign, \
    AssignTarget, SimpleWhitespace, ConcatenatedString, ImportFrom
from libcst.metadata import ParentNodeProvider, ScopeProvider

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.literals import LiteralDuplicationAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets import AssetGroup
from snakepack.assets.python import PythonModule, Python, PythonModuleCst
from snakepack.transformers.python._base import PythonModuleTransformer
from snakepack.transformers.python._renaming import NameRegistry


class HoistLiteralsTransformer(PythonModuleTransformer):
    REQUIRED_ANALYZERS = PythonModuleTransformer.REQUIRED_ANALYZERS + [
        ScopeAnalyzer,
        LiteralDuplicationAnalyzer
    ]

    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        METADATA_DEPENDENCIES = (ParentNodeProvider,)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._name_registry = NameRegistry()
            self._hoisted_literals: Dict[str, Tuple[str, BaseExpression]] = {}
            self._reuse_existing_assignments = False

        def leave_SimpleString(self, original_node: SimpleString, updated_node: SimpleString) -> BaseExpression:
            if self._analyses[LiteralDuplicationAnalyzer].is_part_of_concatenated_string(original_node):
                # don't hoist if string is part of a concatenated string
                return updated_node

            occurrences = self._analyses[LiteralDuplicationAnalyzer].get_occurrences(original_node)

            if len(occurrences) < 2:
                # don't hoist if only used once
                return updated_node

            # check if assignment exists for this value
            scope = self._analyses[ScopeAnalyzer].get_scope_for_node(original_node)
            assignments = self._analyses[LiteralDuplicationAnalyzer].get_preceding_assignments(
                literal_node=original_node,
                scope=scope
            )

            if (
                    self._reuse_existing_assignments
                    and assignments is not None and len(assignments) > 0
                    and all(map(lambda x: self._analyses[ScopeAnalyzer].get_scope_for_node(x) is scope, occurrences))
            ):
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
                    new_identifier = None
                    all_scopes = self._analyses[ScopeAnalyzer].get_all_scopes()

                    while (
                            new_identifier is None
                            or any(map(lambda x: new_identifier in x.assignments, all_scopes))
                    ):
                        # generate new name that is not referenced yet in the current scope
                        new_identifier = self._name_registry.generate_name_for_scope(scope=scope.globals)

                    non_hoisted_char_count = len(updated_node.value) * len(occurrences)
                    assign_char_count = len(updated_node.value) + 1 + len(new_identifier)
                    hoisted_char_count = assign_char_count + (2 * len(new_identifier))

                    if non_hoisted_char_count <= hoisted_char_count:
                        # don't hoist because no size reduction
                        self._name_registry.reset(scope=scope.globals)
                        return updated_node

                    # we'll be using the generated identifier for hoisting
                    self._name_registry.register_name_for_scope(scope=scope.globals, name=new_identifier)

            if not self._reuse_existing_assignments or not use_existing_assignment:
                # mark the literal for hoisting with a new variable assignment
                self._hoisted_literals[updated_node.value] = new_identifier, updated_node
            else:
                # reuse existing assignment

                if (
                        original_node in map(lambda x: x.value, flatten(map(lambda x: x[1], assignments.items())))
                        and all(map(lambda x: self._analyses[ScopeAnalyzer].get_scope_for_node(x) is scope, occurrences))
                ):
                    # do not replace literal with a reference in the first in-scope assignment itself
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

            hoisted = False

            for block_index, stmt_block in enumerate(updated_node.body):
                updated_stmt_block_body = list(stmt_block.body)

                for stmt_index, stmt in enumerate(stmt_block.body):
                    if (
                            not (
                                    isinstance(stmt, ImportFrom)
                                    and isinstance(stmt.module, Name)
                                    and stmt.module.value == '__future__'
                            )
                            and not (
                                    isinstance(stmt, Expr)
                                    and isinstance(stmt.value, SimpleString)
                            )
                    ):
                        # not a from __future__ import or module doc, so we can hoist assign before this stmt
                        updated_stmt_block_body = [
                            *updated_stmt_block_body[:stmt_index],
                            *hoist_assignments,
                            *updated_stmt_block_body[stmt_index:]
                        ]
                        updated_body[block_index] = stmt_block.with_changes(body=updated_stmt_block_body)
                        hoisted = True
                        break

                if hoisted:
                    break

            return updated_node.with_changes(body=updated_body)

    __config_name__ = 'hoist_literals'

