from __future__ import annotations

from typing import Union, Optional, Tuple, Dict, Iterable, Sequence, List, Set

from boltons.iterutils import first, flatten
from libcst import MetadataWrapper, Assign, AnnAssign, SimpleString, VisitorMetadataProvider, AugAssign, Name, \
    BaseExpression, ConcatenatedString
from libcst.metadata import ScopeProvider, ExpressionContextProvider, ParentNodeProvider

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python import PythonModuleCstAnalyzer
from snakepack.assets import Asset, AssetGroup
from snakepack.assets.python import PythonModule, PythonModuleCst


class LiteralDuplicationAnalyzer(PythonModuleCstAnalyzer):
    def analyse(self, subject: Union[Asset, AssetGroup]) -> LiteralDuplicationAnalyzer.Analysis:
        if isinstance(subject, PythonModule):
            metadata = subject.content.metadata_wrapper.resolve_many([
                ParentNodeProvider,
                self._LiteralDuplicationCountProvider,
                self._LiteralAssignmentProvider
            ])

            return LiteralDuplicationAnalyzer.Analysis(
                modules_metadata={
                    subject: metadata
                }
            )
        else:
            raise NotImplementedError

    class Analysis(PythonModuleCstAnalyzer.Analysis):
        def get_num_occurrences(self, module: PythonModule, literal_node: SimpleString) -> Optional[int]:
            if literal_node not in self._modules_metadata[module][LiteralDuplicationAnalyzer._LiteralDuplicationCountProvider]:
                return None

            return self._modules_metadata[module][LiteralDuplicationAnalyzer._LiteralDuplicationCountProvider][literal_node]

        def is_part_of_concatenated_string(self, module, literal_node: SimpleString) -> bool:
            return isinstance(self._modules_metadata[module][ParentNodeProvider][literal_node], ConcatenatedString)

        def get_preceding_assignments(
                self,
                module: PythonModule,
                literal_node: SimpleString
        ) -> Dict[str, Sequence[Union[Assign, AnnAssign, AugAssign]]]:
            for literal, assignments in self._modules_metadata[module][LiteralDuplicationAnalyzer._LiteralAssignmentProvider].items():
                if literal_node.value == literal.value:
                    return assignments

            return None

    class _LiteralDuplicationCountProvider(VisitorMetadataProvider[int]):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._literal_counts: Dict[str, Tuple[int, List[SimpleString]]] = {}

        def visit_SimpleString(self, node: SimpleString) -> Optional[bool]:
            if node.value not in self._literal_counts:
                self._literal_counts[node.value] = (0, [])

            self._literal_counts[node.value] = (self._literal_counts[node.value][0] + 1, self._literal_counts[node.value][1])
            self._literal_counts[node.value][1].append(node)

            for duplicated_node in self._literal_counts[node.value][1]:
                self.set_metadata(duplicated_node, self._literal_counts[node.value][0])

    class _LiteralAssignmentProvider(
        VisitorMetadataProvider[
            Dict[
                str,
                Sequence[
                    Union[Assign, AnnAssign, AugAssign]
                ]
            ]
        ]):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._literal_assignments: Dict[str, Dict[str, List[Union[Assign, AnnAssign, AugAssign]]]] = {}
            self._literals_referenced: Set[str] = set()

        def visit_SimpleString(self, node: SimpleString) -> Optional[bool]:
            self._literals_referenced.add(node.value)

        def visit_Assign(self, node: Assign) -> Optional[bool]:
            if isinstance(node.value, SimpleString):
                for target in node.targets:
                    if isinstance(target.target, Name):
                        self._track_assignment_for_literal(node.value, target.target, node)

                    self._invalidate_previous_assignments(target.target, node.value, node)

        def visit_AnnAssign(self, node: AnnAssign) -> Optional[bool]:
            if isinstance(node.value, SimpleString) and isinstance(node.target, Name):
                self._track_assignment_for_literal(node.value, node.target, node)

            self._invalidate_previous_assignments(node.target, node.value, node)

        def visit_AugAssign(self, node: AugAssign) -> Optional[bool]:
            if isinstance(node.value, SimpleString) and isinstance(node.target, Name):
                self._track_assignment_for_literal(node.value, node.target, node)

            self._invalidate_previous_assignments(node.target, node.value, node)

        def _track_assignment_for_literal(self, literal: SimpleString, name: Name, node: Union[Assign, AnnAssign, AugAssign]):
            if literal.value in self._literals_referenced:
                # don't track assignment as it follows after a reference
                return
            if literal.value not in self._literal_assignments:
                self._literal_assignments[literal.value] = {}

            if name not in self._literal_assignments[literal.value]:
                self._literal_assignments[literal.value][name.value] = []

            self._literal_assignments[literal.value][name.value].append(node)
            self.set_metadata(literal, self._literal_assignments[literal.value])

        def _invalidate_previous_assignments(self, name: Name, value: BaseExpression, node: Union[Assign, AnnAssign, AugAssign]):
            # invalidate literal assignments if their identifier is assigned to again
            invalidate = False

            for literal_value, assignments in self._literal_assignments.items():
                if name.value in assignments:
                    if (isinstance(node, AugAssign) or (isinstance(node, (Assign, AnnAssign)) and
                            (not isinstance(value, SimpleString) or value.value != literal_value))):
                        # invalidate because re-assignment to identifier with another value
                        del self._literal_assignments[literal_value][name.value]
