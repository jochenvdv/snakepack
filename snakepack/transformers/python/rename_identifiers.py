from typing import Optional, Union, Dict, Mapping, Type

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, Name, BaseExpression, CSTNode, Import, ImportFrom, Nonlocal, Param, Global, Module
from libcst.metadata import ExpressionContextProvider, ExpressionContext, ScopeProvider, ParentNodeProvider, Scope, \
    GlobalScope, ClassScope, Assignment, BuiltinScope

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
            self._no_renames = set()

        def visit_Import(self, node: Import) -> Optional[bool]:
            # don't rename import identifiers
            return False

        def visit_ImportFrom(self, node: ImportFrom) -> Optional[bool]:
            # don't rename import identifiers
            return False

        def visit_Global(self, node: Global) -> Optional[bool]:
            if self._options.only_rename_locals:
                # identifier wasn't renamed in scope above, so won't be renaming it here
                return False

        def visit_Nonlocal(self, node: Nonlocal) -> Optional[bool]:
            for name_item in node.names:
                name = name_item.name.value

                if name in self._excluded_names or name in self._no_renames:
                    continue

                scope = self._analyses[ScopeAnalyzer].get_scope_for_node(node)
                renamed_in_scope = self._identifier_renamed_in_scope(name, scope)

                if renamed_in_scope is None:
                    # identifier wasn't renamed in scope above, so won't be renaming it here
                    return False

                # mark nonlocal name for renaming
                self._renames[name_item.name] = self._renames_scope_map[renamed_in_scope][name]
                self._name_registry.register_name_for_scope(scope=scope, name=name)

        def visit_Name(self, node: Name) -> Optional[bool]:
            if node in self._renames or node in self._no_renames:
                # already marked this identifier to (not) be renamed
                return

            if node.value in self._excluded_names:
                # identifier is excluded from renaming
                return self._dont_rename(node)

            if self._options.only_rename_locals and not self._analyses[ScopeAnalyzer].is_in_local_scope(node):
                return self._dont_rename(node)

            if self._analyses[ScopeAnalyzer].is_attribute(node):
                # don't rename class attributes (nearly impossible to find all references through static analysis)
                return self._dont_rename(node)

            if self._analyses[ScopeAnalyzer].is_type_annotation(node):
                # don't rename type annotations
                return self._dont_rename(node)

            if self._analyses[ScopeAnalyzer].is_keyword_arg(node):
                # don't rename keyword argument names
                return self._dont_rename(node)

            if self._analyses[ImportGraphAnalyzer].identifier_imported_in_module(node.value, self._subject):
                # don't rename variable name as it is imported
                return self._dont_rename(node)

            if (
                    not self._options.only_rename_locals
                    and self._analyses[ImportGraphAnalyzer].import_graph_known
                    and len(self._analyses[ImportGraphAnalyzer].get_importing_modules(self._subject, node.value)) > 0
            ):
                # don't rename because this identifier is imported in another module
                return self._dont_rename(node)

            scope = self._analyses[ScopeAnalyzer].get_scope_for_node(node)

            if isinstance(scope, BuiltinScope):
                # don't rename builtins
                return self._dont_rename(node)

            if (
                    not self._options.only_rename_locals
                    and not self._analyses[ImportGraphAnalyzer].import_graph_known
                    and isinstance(scope, (GlobalScope, ClassScope))
            ):
                # don't rename because import graph is unknown and node is in global or class scope
                return self._dont_rename(node)

            current_scope = scope
            to_rename = []
            done = False

            while not done:
                for assignment in current_scope.assignments[node.value]:
                    if not self._options.only_rename_locals or self._analyses[ScopeAnalyzer].is_in_local_scope(assignment.node):
                        to_rename.append(assignment)

                if isinstance(current_scope, (BuiltinScope, GlobalScope)):
                    done = True

                current_scope = current_scope.parent

            if not self._options.only_rename_locals or not any(map(lambda x: isinstance(x.node, Param), to_rename)):
                for assignment in to_rename:
                    if assignment.node not in self._no_renames:
                        self._rename_identifier(node, scope, assignment)

        def leave_Name(self, original_node: Name, updated_node: Name) -> BaseExpression:
            if original_node in self._renames and updated_node.value not in self._excluded_names:
                return updated_node.with_changes(value=self._renames[original_node])

            return updated_node

        def _rename_identifier(self, node: Name, scope: Scope, assignment: Optional[Assignment] = None):
            if renamed_in_scope := self._identifier_renamed_in_scope(node.value, scope):
                # use generated identifier for previous assignment
                new_name = self._renames_scope_map[renamed_in_scope][node.value]
            else:
                new_name = None

                while (
                        new_name is None
                        or (new_name != node.value and len(scope.accesses[new_name]) > 0)
                        or new_name in scope
                        or self._identifier_renamed_in_scope(new_name, scope, by_new_name=True) is not None
                ):
                    # generate new name that is not referenced yet in the current scope
                    new_name = self._name_registry.generate_name_for_scope(scope=scope)

            if len(new_name) >= len(node.value):
                # don't rename because new identifier is not shorter
                return self._dont_rename(node)

            self._renames[node] = new_name

            if scope not in self._renames_scope_map:
                self._renames_scope_map[scope] = {}

            self._renames_scope_map[scope][node.value] = new_name
            self._name_registry.register_name_for_scope(scope=scope, name=new_name)

            if assignment is not None:
                for access in assignment.references:
                    if access.node not in self._no_renames:
                        self._renames[access.node] = new_name

        def _identifier_renamed_in_scope(self, name: str, scope: Scope, by_new_name=False) -> Optional[Scope]:
            current_scope = scope
            done = False

            while not done:
                if current_scope in self._renames_scope_map:
                    if not by_new_name and name in self._renames_scope_map[current_scope]:
                        return current_scope

                    if by_new_name and name in self._renames_scope_map[current_scope].values():
                        return current_scope

                if isinstance(current_scope, GlobalScope):
                    done = True

                current_scope = current_scope.parent

            return None

        def _dont_rename(self, node):
            self._no_renames.add(node)

    class Options(PythonModuleTransformer.Options):
        only_rename_locals: bool = True

    __config_name__ = 'rename_identifiers'
