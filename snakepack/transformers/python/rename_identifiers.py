from typing import Optional, Union, Dict, Mapping, Type

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, Name, BaseExpression, CSTNode, Import, ImportFrom, Nonlocal
from libcst.metadata import ExpressionContextProvider, ExpressionContext, ScopeProvider, ParentNodeProvider, Scope, \
    GlobalScope, ClassScope

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets import AssetGroup
from snakepack.assets.python import PythonModule, Python, PythonModuleCst
from snakepack.transformers.python._base import PythonModuleTransformer
from snakepack.transformers.python._renaming import NameRegistry


class RenameIdentifiersTransformer(PythonModuleTransformer):
    REQUIRED_ANALYZERS = PythonModuleTransformer.REQUIRED_ANALYZERS + [
        ScopeAnalyzer,
        ImportGraphAnalyzer
    ]

    def transform(
            self,
            analyses: Mapping[Type[Analyzer], Analyzer.Analysis],
            subject: Union[PythonModule, AssetGroup[Python]]
    ) -> Union[PythonModule, AssetGroup[Python]]:
        if isinstance(subject, PythonModule):
            transformer = self._CstTransformer(
                subject=subject,
                options=self._options,
                analyses=analyses,
                transformer=self
            )
            subject.content = PythonModuleCst(cst=subject.content.cst.visit(transformer))

        return subject

    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._name_registry = NameRegistry()
            self._renames: Dict[CSTNode, str] = {}
            self._renames_scope_map: Dict[Scope, Dict[str, str]] = {}
            self._excluded_names = set()

        def visit_Import(self, node: Import) -> Optional[bool]:
            # don't rename import identifiers
            return False

        def visit_ImportFrom(self, node: ImportFrom) -> Optional[bool]:
            # don't rename import identifiers
            return False

        def visit_Nonlocal(self, node: Nonlocal) -> Optional[bool]:
            # exclude identifiers referenced by nonlocal statements (libcst-limitation)
            for name_item in node.names:
                name = name_item.name.value

                if name in self._excluded_names:
                    continue

                current_scope = None

                while not isinstance(current_scope, GlobalScope):
                    if current_scope is None:
                        current_scope = self._analyses[ScopeAnalyzer].get_scope_for_node(node)
                    else:
                        current_scope = current_scope.parent

                    if current_scope in self._renames_scope_map and name in self._renames_scope_map[current_scope]:
                        # mark nonlocal name for renaming
                        self._renames[name_item.name] = self._renames_scope_map[current_scope][name]
                        self._name_registry.register_name_for_scope(scope=current_scope, name=name)

        def visit_Name(self, node: Name) -> Optional[bool]:
            if node in self._renames:
                # already marked this identifier to be renamed
                return

            if node.value in self._excluded_names:
                # identifier is excluded from renaming
                return

            if self._analyses[ScopeAnalyzer].is_attribute(node):
                # don't rename class attributes (nearly impossible to find all references through static analysis)
                return

            if (
                    self._analyses[ImportGraphAnalyzer].import_graph_known
                    and len(self._analyses[ImportGraphAnalyzer].get_importing_modules(self._subject, node.value)) > 0
            ):
                # don't rename because this identifier is imported in another module
                return

            scope = self._analyses[ScopeAnalyzer].get_scope_for_node(node)

            if not self._analyses[ImportGraphAnalyzer].import_graph_known and isinstance(scope, (GlobalScope, ClassScope)):
                # don't rename because import graph is unknown and node is in global or class scope
                return

            for assignment in scope.assignments[node]:
                if assignment.name is node.value:
                    new_name = None

                    while new_name is None or (new_name != node.value and len(scope.accesses[new_name]) > 0):
                        # generate new name that is not referenced yet in the current scope
                        new_name = self._name_registry.generate_name_for_scope(scope=scope)

                    self._renames[node] = new_name

                    if scope not in self._renames_scope_map:
                        self._renames_scope_map[scope] = {}

                    self._renames_scope_map[scope][node.value] = new_name
                    self._name_registry.register_name_for_scope(scope=scope, name=new_name)

                    for access in assignment.references:
                        self._renames[access.node] = new_name

        def leave_Name(self, original_node: Name, updated_node: Name) -> BaseExpression:
            if original_node in self._renames and updated_node.value not in self._excluded_names:
                return updated_node.with_changes(value=self._renames[original_node])

            return updated_node


    __config_name__ = 'rename_identifiers'
