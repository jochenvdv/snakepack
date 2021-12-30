from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, ClassDef, Name

from snakepack.transformers.python._base import PythonModuleTransformer, BatchablePythonModuleTransformer


class RemoveObjectBaseTransformer(BatchablePythonModuleTransformer):
    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def leave_ClassDef(
                self, original_node: ClassDef, updated_node: ClassDef
        ) -> Union[BaseStatement, FlattenSentinel[BaseStatement], RemovalSentinel]:
            updated_bases = [
                base for base in original_node.bases
                if not isinstance(base.value, Name) or base.value.value != 'object'
            ]

            return updated_node.with_changes(
                bases=updated_bases,
                lpar=MaybeSentinel.DEFAULT,
                rpar=MaybeSentinel.DEFAULT
            )


    __config_name__ = 'remove_object_base'

