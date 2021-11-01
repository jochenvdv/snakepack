from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, Assign, BaseSmallStatement, AssignTarget, Call, BaseExpression, SimpleWhitespace, TrailingWhitespace, \
    ParenthesizedWhitespace, Arg, Comma, AssignEqual, IndentedBlock, BaseSuite, Module, EmptyLine, Semicolon, Del, \
    Assert, Global, Import, ImportFrom, Nonlocal, Raise, Return, Colon, AnnAssign, Annotation, For, FunctionDef, If, \
    Try, While, ExceptHandler, AsName, With, Decorator, Else, Finally, Param

from snakepack.transformers.python._base import PythonModuleCstTransformer


class RemoveWhitespaceTransformer(PythonModuleCstTransformer):
    class _CstTransformer(CSTTransformer):
        def leave_AssignTarget(
                self, original_node: AssignTarget, updated_node: AssignTarget
        ) -> Union[AssignTarget, FlattenSentinel[AssignTarget], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_before_equal', 'whitespace_after_equal')

        def leave_Call(self, original_node: Call, updated_node: Call) -> BaseExpression:
            return self._remove_whitespace(updated_node, 'whitespace_before_args', 'whitespace_after_func')

        def leave_Arg(self, original_node: Arg, updated_node: Arg) -> Union[Arg, FlattenSentinel[Arg], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_after_star', 'whitespace_after_arg')

        def leave_Comma(self, original_node: Comma, updated_node: Comma) -> Union[Comma, MaybeSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_before', 'whitespace_after')

        def leave_AssignEqual(
                self, original_node: AssignEqual, updated_node: AssignEqual
        ) -> Union[AssignEqual, MaybeSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_before', 'whitespace_after')

        def leave_IndentedBlock(self, original_node: IndentedBlock, updated_node: IndentedBlock) -> BaseSuite:
            return updated_node.with_changes(
                body=self._merge_statement_block(updated_node.body)
            )

        def leave_Module(self, original_node: Module, updated_node: Module) -> Module:
            return updated_node.with_changes(
                body=self._merge_statement_block(updated_node.body),
                default_indent=' ',
                default_newline='\n',
                has_trailing_newline=False
            )

        def leave_TrailingWhitespace(
                self, original_node: TrailingWhitespace, updated_node: TrailingWhitespace
        ) -> TrailingWhitespace:
            return updated_node.with_deep_changes(updated_node.whitespace, value='')

        def leave_EmptyLine(
                self, original_node: EmptyLine, updated_node: EmptyLine
        ) -> Union[EmptyLine, FlattenSentinel[EmptyLine], RemovalSentinel]:
            if updated_node.comment is None:
                return RemovalSentinel.REMOVE

            return updated_node.with_changes(
                whitespace=updated_node.whitespace.with_changes(
                    value=''
                ),
                newline=updated_node.newline.with_changes(
                    value=None
                )
            )

        def leave_Del(
                self, original_node: Del, updated_node: Del
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_after_del', semantic=True)

        def leave_Assert(
                self, original_node: Assert, updated_node: Assert
        ) -> Union[ BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_after_assert', semantic=True)

        def leave_Global(
                self, original_node: Global, updated_node: Global
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_after_global', semantic=True)

        def leave_Import(
                self, original_node: Import, updated_node: Import
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_after_import', semantic=True)

        def leave_ImportFrom(
                self, original_node: ImportFrom, updated_node: ImportFrom
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            return self._remove_whitespace(
                updated_node,
                'whitespace_after_from',
                'whitespace_before_import',
                'whitespace_after_import',
                semantic=True
            )

        def leave_Nonlocal(
                self, original_node: Nonlocal, updated_node: Nonlocal
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_after_nonlocal', semantic=True)

        def leave_Raise(
                self, original_node: Raise, updated_node: Raise
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            semantic = updated_node.exc is not None
            return self._remove_whitespace(updated_node, 'whitespace_after_raise', semantic=semantic)

        def leave_Return(
                self, original_node: Return, updated_node: Return
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            semantic = updated_node.value is not None
            return self._remove_whitespace(updated_node, 'whitespace_after_return', semantic=semantic)

        def leave_Annotation(self, original_node: Annotation, updated_node: Annotation) -> Annotation:
            return self._remove_whitespace(updated_node, 'whitespace_before_indicator', 'whitespace_after_indicator')

        def leave_For(
                self, original_node: For, updated_node: For
        ) -> Union[BaseStatement, FlattenSentinel[BaseStatement], RemovalSentinel]:
            return self._remove_whitespace(
                self._remove_whitespace(
                    updated_node,
                    'whitespace_before_colon'
                ),
                'whitespace_after_for',
                'whitespace_before_in',
                'whitespace_after_in',
                semantic=True
            )

        def leave_FunctionDef(
                self, original_node: FunctionDef, updated_node: FunctionDef
        ) -> Union[BaseStatement, FlattenSentinel[BaseStatement], RemovalSentinel]:
            return self._remove_whitespace(
                self._remove_whitespace(
                    updated_node,
                    'whitespace_after_name',
                    'whitespace_before_params',
                    'whitespace_before_colon'
                ),
                'whitespace_after_def',
                semantic=True
            )

        def leave_If(
                self, original_node: If, updated_node: If
        ) -> Union[BaseStatement, FlattenSentinel[BaseStatement], RemovalSentinel]:
            return self._remove_whitespace(
                self._remove_whitespace(
                    updated_node,
                    'whitespace_after_test'
                ),
                'whitespace_before_test',
                semantic=True
            )

        def leave_Try(
                self, original_node: Try, updated_node: Try
        ) -> Union[BaseStatement, FlattenSentinel[BaseStatement], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_before_colon')

        def leave_While(
                self, original_node: While, updated_node: While
        ) -> Union[BaseStatement, FlattenSentinel[BaseStatement], RemovalSentinel]:
            return self._remove_whitespace(
                self._remove_whitespace(
                    updated_node,
                    'whitespace_before_colon'
                ),
                'whitespace_after_while',
                semantic=True
            )

        def leave_AsName(self, original_node: AsName, updated_node: AsName) -> AsName:
            return self._remove_whitespace(
                updated_node,
                'whitespace_before_as',
                'whitespace_after_as',
                semantic=True
            )

        def leave_ExceptHandler(
                self, original_node: ExceptHandler, updated_node: ExceptHandler
        ) -> Union[ExceptHandler, FlattenSentinel[ExceptHandler], RemovalSentinel]:
            semantic = updated_node.type is not None

            return self._remove_whitespace(
                self._remove_whitespace(
                    updated_node,
                    'whitespace_before_colon'
                ),
                'whitespace_after_except',
                semantic=semantic
            )

        def leave_With(
                self, original_node: With, updated_node: With
        ) -> Union[BaseStatement, FlattenSentinel[BaseStatement], RemovalSentinel]:
            return self._remove_whitespace(
                self._remove_whitespace(
                    updated_node,
                    'whitespace_before_colon'
                ),
                'whitespace_after_with',
                semantic=True
            )

        def leave_Decorator(
                self, original_node: Decorator, updated_node: Decorator
        ) -> Union[Decorator, FlattenSentinel[Decorator], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_after_at')

        def leave_Else(self, original_node: Else, updated_node: Else) -> Else:
            return self._remove_whitespace(updated_node, 'whitespace_before_colon')

        def leave_Finally(self, original_node: Finally, updated_node: Finally) -> Finally:
            return self._remove_whitespace(updated_node, 'whitespace_before_colon')

        def leave_Semicolon(self, original_node: Semicolon, updated_node: Semicolon) -> Union[Semicolon, MaybeSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_before', 'whitespace_after')

        def leave_Colon(self, original_node: Colon, updated_node: Colon) -> Union[Colon, MaybeSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_before', 'whitespace_after')

        @staticmethod
        def _remove_whitespace(node, *attrs, semantic=False):
            changes = {}

            for attr in attrs:
                whitespace = getattr(node, attr)

                if isinstance(whitespace, SimpleWhitespace):
                    if semantic:
                        new_value = ' '
                    else:
                        new_value = ''

                    whitespace = whitespace.with_changes(value=new_value)
                elif isinstance(whitespace, ParenthesizedWhitespace):
                    # todo
                    raise NotImplementedError

                changes[attr] = whitespace

            return node.with_changes(**changes)

        @staticmethod
        def _merge_statement_lines(lines, leading_lines, trailing_whitespace):
            assert len(lines) > 0
            merged_body = []

            for line_index, line in enumerate(lines):
                for stmt_index, statement in enumerate(line.body):
                    if line_index == len(lines) - 1 and stmt_index == len(line.body) - 1:
                        # last statement
                        statement = statement.with_changes(
                            semicolon=MaybeSentinel.DEFAULT
                        )
                    else:
                        statement = statement.with_changes(
                            semicolon=Semicolon(
                                whitespace_before=SimpleWhitespace(value=''),
                                whitespace_after=SimpleWhitespace(value='')
                            )
                        )
                    merged_body.append(statement)

            if trailing_whitespace is None:
                trailing_whitespace = TrailingWhitespace()

            return SimpleStatementLine(
                body=merged_body,
                leading_lines=leading_lines,
                trailing_whitespace=trailing_whitespace
            )

        @classmethod
        def _merge_statement_block(cls, statements):
            updated_body = []
            collapse_queue = []
            leading_lines = []

            for statement in statements:
                if isinstance(statement, SimpleStatementLine):
                    if not all(map(lambda x: x.comment is None, statement.leading_lines)):
                        # need to merge previous lines because this statement contains leading comments
                        updated_body.append(
                            cls._merge_statement_lines(
                                lines=collapse_queue,
                                leading_lines=leading_lines,
                                trailing_whitespace=statement.trailing_whitespace
                            )
                        )

                        if statement.trailing_whitespace.comment is not None:
                            # can't collapse with following statement because of trailing whitespace
                            collapse_queue.clear()
                            leading_lines.clear()
                        else:
                            # can possibly be merged with following lines
                            collapse_queue = [statement]
                            leading_lines = [*statement.leading_lines]
                    elif statement.trailing_whitespace.comment is None:
                        # can possibly be merged with next lines
                        collapse_queue.append(statement)
                    else:
                        # can't collapse with following statement because of trailing whitespace
                        collapse_queue.append(statement)
                        updated_body.append(
                            cls._merge_statement_lines(
                                lines=collapse_queue,
                                leading_lines=leading_lines,
                                trailing_whitespace=statement.trailing_whitespace
                            )
                        )
                        collapse_queue.clear()
                        leading_lines.clear()
                else:
                    #  can't merge because not simple statement line, merge previous lines and simply append
                    if len(collapse_queue) > 0:
                        # need to do a final merge of collapse queue
                        updated_body.append(
                            cls._merge_statement_lines(
                                lines=collapse_queue,
                                leading_lines=leading_lines,
                                trailing_whitespace=None
                            )
                        )
                        collapse_queue.clear()
                        leading_lines.clear()

                    updated_body.append(statement)

            if len(collapse_queue) > 0:
                # need to do a final merge of collapse queue
                updated_body.append(
                    cls._merge_statement_lines(
                        lines=collapse_queue,
                        leading_lines=leading_lines,
                        trailing_whitespace=None
                    )
                )

            return updated_body

    __config_name__ = 'remove_whitespace'
