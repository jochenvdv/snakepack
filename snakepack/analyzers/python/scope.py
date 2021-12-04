from __future__ import annotations

import string
from collections import deque
from itertools import permutations
from typing import Union, List, Iterable, Optional, Sequence

from libcst import MetadataWrapper, CSTNode, Name, Attribute, ClassDef, FunctionDef
from libcst.metadata import ScopeProvider, ExpressionContextProvider
from libcst.metadata import Scope as CstScope

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python import PythonModuleCstAnalyzer
from snakepack.assets import Asset, AssetGroup
from snakepack.assets.python import PythonModule, PythonModuleCst
from snakepack.config.options import Selectable
from snakepack.config.types import Selector, FullyQualifiedPythonName


class ScopeAnalyzer(PythonModuleCstAnalyzer):
    def analyse(self, subject: Union[Asset, AssetGroup]) -> ScopeAnalyzer.Analysis:
        if isinstance(subject, PythonModule):
            metadata = subject.content.metadata_wrapper.resolve(ScopeProvider)

            return ScopeAnalyzer.Analysis(
                modules_metadata={
                    subject: metadata
                }
            )
        else:
            raise NotImplementedError

    class Analysis(PythonModuleCstAnalyzer.Analysis):
        def __init__(self, module_metadata, *args, **kwargs):
            pass

        def get_fully_qualified_names(
                self, module: PythonModule, node: Union[Name, Attribute, ClassDef, FunctionDef]
        ) -> Iterable[FullyQualifiedPythonName]:
            qualnames = self._modules_metadata[module][node].get_qualified_names_for(node)

            return set(
                map(
                    lambda x: FullyQualifiedPythonName(f"{module.full_name}:{x.name.replace('<locals>.', '')}"),
                    qualnames
                )
            )

        def get_next_possible_identifier(self) -> str:
            pass

        def register_identifier(self, identifier: str):
            pass

        def get_scope(self, node: CSTNode) -> Scope:
            pass

        def is_referenced(self, identifier, scope: Optional[Scope]) -> bool:
            pass

        def get_references(self, identifier, scope: Optional[Scope]):
            pass

        def get_assignments(self, identifier, scope: Optional[Scope]):
            pass


class Identifier(Selectable):
    def __init__(self, name: str, assignments: List[Assignment], references: List[Reference], scopes: List[Scope]):
        self._name = name
        self._assignments = assignments
        self._references = references
        self._referencable_scopes = scopes

    @property
    def name(self) -> str:
        return self._name

    @property
    def assignments(self) -> List[Assignment]:
        return self._assignments

    @property
    def references(self) -> List[Reference]:
        return self._references

    @property
    def referencable_scopes(self) -> List[Scope]:
        return self._referencable_scopes

    def matches(self, selector: Selector) -> bool:
        if not isinstance(selector, FullyQualifiedPythonName):
            return False

    def register_assignment(self, assignment: Assignment):
        assignment.identifier = self
        self._assignments.append(assignment)

    def register_reference(self, reference: Reference):
        reference.identifier = self
        self._references.append(reference)

    @staticmethod
    def generate():
        first_chars = string.ascii_letters
        chars = first_chars + string.digits

        yield from first_chars
        size = 2

        while True:
            yield from map(lambda x: ''.join(x), permutations(chars, size))
            size += 1


class Reference:
    def __init__(self, scope: Scope, node: CSTNode, identifier: Optional[Identifier] = None):
        self._identifier = identifier
        self._scope = scope

    @property
    def identifier(self) -> Identifier:
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        self._identifier = identifier

    @property
    def scope(self) -> Scope:
        return self._scope


class Assignment:
    def __init__(self, scope: Scope, node: CSTNode, identifier: Optional[Identifier] = None):
        self._identifier = identifier
        self._scope = scope
        self._node = node

    @property
    def identifier(self) -> Identifier:
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        self._identifier = identifier

    @property
    def scope(self) -> Scope:
        return self._scope

    @property
    def node(self) -> CSTNode:
        return self._node


class Scope:
    def __init__(self, assignments: List[Assignment], references: List[Reference], node: CSTNode):
        self._assignments = assignments
        self._references = references
        self._node = node
        self._ident_generator = None

    @property
    def assignments(self) -> List[Assignment]:
        return self._assignments

    @property
    def references(self) -> List[Reference]:
        return self._references

    @property
    def node(self) -> CSTNode:
        return self._node

    def generate_identifier(self) -> str:
        if self._ident_generator is None:
            self._ident_generator = (Identifier.generate(), deque())

        if len(self._ident_generator[1]) > 0:
            name = self._ident_generator[1][-1]
        else:
            name = next(self._ident_generator[0])
            self._ident_generator.appendleft(name)

        return name

    def register_assignment(self, name: str, assignment_node: CSTNode):
        assert len(self._ident_generator[1]) > 0

        assignment = Assignment(
            scope=self,
            node=assignment_node
        )
        identifier = Identifier(
            name=self._ident_generator[1].pop(),
            scopes=[self]
        )

        assert identifier.name == name

        identifier.register_assignment(assignment)
        self._assignments.append(assignment)

    def register_reference(self, name: str, reference_node: CSTNode):
        assert len(self._ident_generator[1]) > 0

        assignment = Reference(
            scope=self,
            node=reference_node
        )
        identifier = Identifier(
            name=name,
            scopes=[self]
        )
        assert identifier.name == name

        identifier.assignments.append(assignment)
        self._assignments.append(assignment)
