from __future__ import annotations

from typing import Union, Optional, Tuple, Dict, Iterable, Sequence, List

from libcst import MetadataWrapper, Assign, AnnAssign, SimpleString, VisitorMetadataProvider
from libcst.metadata import ScopeProvider, ExpressionContextProvider

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python import PythonModuleCstAnalyzer
from snakepack.assets import Asset, AssetGroup
from snakepack.assets.python import PythonModule, PythonModuleCst


class LiteralDuplicationAnalyzer(PythonModuleCstAnalyzer):
    def analyse(self, subject: Union[Asset, AssetGroup]) -> LiteralDuplicationAnalyzer.Analysis:
        if isinstance(subject, PythonModule):
            metadata = subject.content.metadata_wrapper.resolve(self._LiteralDuplicationCountProvider)

            return LiteralDuplicationAnalyzer.Analysis(
                modules_metadata={
                    subject: metadata
                }
            )
        else:
            raise NotImplementedError

    class Analysis(PythonModuleCstAnalyzer.Analysis):
        def get_num_occurrences(self, module: PythonModule, literal_node: SimpleString) -> Optional[int]:
            if literal_node not in self._modules_metadata[module]:
                return None

            return self._modules_metadata[module][literal_node][0]

    class _LiteralDuplicationCountProvider(VisitorMetadataProvider[Tuple[int, Optional[str]]]):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._literal_counts: Dict[str, Tuple[int, List[SimpleString]]] = {}

        def visit_SimpleString(self, node: SimpleString) -> Optional[bool]:
            if node.value not in self._literal_counts:
                self._literal_counts[node.value] = (0, [])

            self._literal_counts[node.value] = (self._literal_counts[node.value][0] + 1, self._literal_counts[node.value][1])
            self._literal_counts[node.value][1].append(node)

            for duplicated_node in self._literal_counts[node.value][1]:
                self.set_metadata(duplicated_node, (self._literal_counts[node.value][0], None))

