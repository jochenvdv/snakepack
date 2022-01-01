from typing import Optional, Union, cast, Sequence

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, Assign, BaseSmallStatement, AssignTarget, Call, BaseExpression, SimpleWhitespace, TrailingWhitespace, \
    ParenthesizedWhitespace, Arg, Comma, AssignEqual, IndentedBlock, BaseSuite, Module, EmptyLine, Semicolon, Del, \
    Assert, Global, Import, ImportFrom, Nonlocal, Raise, Return, Colon, AnnAssign, Annotation, For, FunctionDef, If, \
    Try, While, ExceptHandler, AsName, With, Decorator, Else, Finally, Param, SimpleStatementSuite, Newline, \
    Asynchronous, Await, Yield, From, IfExp, Lambda, ConcatenatedString, FormattedStringExpression, \
    BaseFormattedStringContent, StarredElement, BaseElement, DictElement, BaseDictElement, LeftParen, RightParen, \
    LeftSquareBracket, RightSquareBracket, LeftCurlyBrace, RightCurlyBrace, StarredDictElement, DictComp, CompFor, \
    CompIf, Subscript, UnaryOperation, Not, BooleanOperation, BinaryOperation, Comparison, ComparisonTarget, In, Is, \
    NotIn, IsNot, CSTValidationError

from snakepack.transformers.python._base import PythonModuleTransformer, BatchablePythonModuleTransformer


class RemoveWhitespaceTransformer(BatchablePythonModuleTransformer):
    class _CstTransformer(PythonModuleTransformer._CstTransformer):
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
            changed_node = updated_node.with_changes(
                body=self._merge_statement_block(updated_node.body)
            )

            if len(changed_node.body) == 1 and isinstance(changed_node.body[0], SimpleStatementLine):
                # all small statements that we can collapse into a single line statement suite
                changed_node = SimpleStatementSuite(
                    body=changed_node.body[0].body,
                    leading_whitespace=SimpleWhitespace(
                        value=''
                    ),
                    trailing_whitespace=TrailingWhitespace(
                        whitespace=SimpleWhitespace(
                            value=''
                        ),
                        newline=Newline(
                            value=None
                        )
                    )
                )

            return changed_node

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

        def leave_Comment(self, original_node: Comment, updated_node: Comment) -> Comment:
            return updated_node.with_changes(
                value=f"#{updated_node.value[1:].strip()}"
            )

        def leave_Asynchronous(self, original_node: Asynchronous, updated_node: Asynchronous) -> Asynchronous:
            return self._remove_whitespace(updated_node, 'whitespace_after', semantic=True)

        def leave_SimpleStatementSuite(
                self,
                original_node: SimpleStatementSuite,
                updated_node: SimpleStatementSuite,
        ) -> BaseSuite:
            return updated_node.with_deep_changes(updated_node.leading_whitespace, value='')

        def leave_Await(self, original_node: Await, updated_node: Await) -> BaseExpression:
            return self._remove_whitespace(updated_node, 'whitespace_after_await', semantic=True)

        def leave_Yield(self, original_node: Yield, updated_node: Yield) -> BaseExpression:
            semantic = updated_node.value is not None
            return self._remove_whitespace(updated_node, 'whitespace_after_yield', semantic=semantic)

        def leave_From(self, original_node: From, updated_node: From) -> From:
            return self._remove_whitespace(
                updated_node,
                'whitespace_before_from',
                'whitespace_after_from',
                semantic=True
            )

        def leave_IfExp(self, original_node: IfExp, updated_node: IfExp) -> BaseExpression:
            return self._remove_whitespace(
                updated_node,
                'whitespace_before_if',
                'whitespace_after_if',
                'whitespace_before_else',
                'whitespace_after_else',
                semantic=True
            )

        def leave_Lambda(self, original_node: Lambda, updated_node: Lambda) -> BaseExpression:
            semantic = (
                    len(updated_node.params.params) > 0 or
                    len(updated_node.params.kwonly_params) > 0 or
                    len(updated_node.params.posonly_params) > 0 or
                    updated_node.params.star_arg is not None or
                    updated_node.params.star_kwarg is not None
            )

            return self._remove_whitespace(updated_node, 'whitespace_after_lambda', semantic=semantic)

        def leave_Param(
                self, original_node: Param, updated_node: Param
        ) -> Union[Param, MaybeSentinel, FlattenSentinel[Param], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_after_star', 'whitespace_after_param')

        def leave_ConcatenatedString(
                self, original_node: ConcatenatedString, updated_node: ConcatenatedString
        ) -> BaseExpression:
            return self._remove_whitespace(updated_node, 'whitespace_between')

        def leave_FormattedStringExpression(
                self,
                original_node: FormattedStringExpression,
                updated_node: FormattedStringExpression,
        ) -> Union[BaseFormattedStringContent, FlattenSentinel[BaseFormattedStringContent], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_before_expression', 'whitespace_after_expression')

        def leave_StarredElement(
                self, original_node: StarredElement, updated_node: StarredElement
        ) -> Union[BaseElement, FlattenSentinel[BaseElement], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_before_value')

        def leave_DictElement(
                self, original_node: DictElement, updated_node: DictElement
        ) -> Union[BaseDictElement, FlattenSentinel[BaseDictElement], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_before_colon', 'whitespace_after_colon')

        def leave_LeftParen(
                self, original_node: LeftParen, updated_node: LeftParen
        ) -> Union[LeftParen, MaybeSentinel, FlattenSentinel[LeftParen], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_after')

        def leave_RightParen(
                self, original_node: RightParen, updated_node: RightParen
        ) -> Union[RightParen, MaybeSentinel, FlattenSentinel[RightParen], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_before')

        def leave_LeftSquareBracket(
                self, original_node: LeftSquareBracket, updated_node: LeftSquareBracket
        ) -> LeftSquareBracket:
            return self._remove_whitespace(updated_node, 'whitespace_after')

        def leave_RightSquareBracket(
                self, original_node: RightSquareBracket, updated_node: RightSquareBracket
        ) -> RightSquareBracket:
            return self._remove_whitespace(updated_node, 'whitespace_before')

        def leave_LeftCurlyBrace(
                self, original_node: LeftCurlyBrace, updated_node: LeftCurlyBrace
        ) -> LeftCurlyBrace:
            return self._remove_whitespace(updated_node, 'whitespace_after')

        def leave_RightCurlyBrace(
                self, original_node: RightCurlyBrace, updated_node: RightCurlyBrace
        ) -> RightCurlyBrace:
            return self._remove_whitespace(updated_node, 'whitespace_before')

        def leave_StarredDictElement(
                self, original_node: StarredDictElement, updated_node: StarredDictElement
        ) -> Union[BaseDictElement, FlattenSentinel[BaseDictElement], RemovalSentinel]:
            return self._remove_whitespace(updated_node, 'whitespace_before_value')

        def leave_DictComp(self, original_node: DictComp, updated_node: DictComp) -> BaseExpression:
            return self._remove_whitespace(updated_node, 'whitespace_before_colon', 'whitespace_after_colon')

        def leave_CompFor(self, original_node: CompFor, updated_node: CompFor) -> CompFor:
            return self._remove_whitespace(
                updated_node,
                'whitespace_before',
                'whitespace_after_for',
                'whitespace_before_in',
                'whitespace_after_in',
                semantic=True
            )

        def leave_CompIf(self, original_node: CompIf, updated_node: CompIf) -> CompIf:
            return self._remove_whitespace(
                updated_node,
                'whitespace_before',
                'whitespace_before_test',
                semantic=True
            )

        def leave_Subscript(self, original_node: Subscript, updated_node: Subscript) -> BaseExpression:
            return self._remove_whitespace(updated_node, 'whitespace_after_value')

        def leave_UnaryOperation(self, original_node: UnaryOperation, updated_node: UnaryOperation) -> BaseExpression:
            semantic = isinstance(updated_node.operator, Not)

            return updated_node.with_changes(
                operator=self._remove_whitespace(updated_node.operator, 'whitespace_after', semantic=semantic)
            )

        def leave_BooleanOperation(
            self, original_node: BooleanOperation, updated_node: BooleanOperation
        ) -> BaseExpression:
            return updated_node.with_changes(
                operator=self._remove_whitespace(
                    updated_node.operator,
                    'whitespace_before',
                    'whitespace_after',
                    semantic=True
                )
            )

        def leave_BinaryOperation(
                self, original_node: BinaryOperation, updated_node: BinaryOperation
        ) -> BaseExpression:
            return updated_node.with_changes(
                operator=self._remove_whitespace(
                    updated_node.operator,
                    'whitespace_before',
                    'whitespace_after'
                )
            )

        def leave_ComparisonTarget(
                self, original_node: ComparisonTarget, updated_node: ComparisonTarget
        ) -> Union[ComparisonTarget, FlattenSentinel[ComparisonTarget], RemovalSentinel]:
            semantic = (isinstance(updated_node.operator, In) or
                        isinstance(updated_node.operator, Is) or
                        isinstance(updated_node.operator, NotIn) or
                        isinstance(updated_node.operator, IsNot))

            changed_node = updated_node.with_changes(
                operator=self._remove_whitespace(
                    updated_node.operator,
                    'whitespace_before',
                    'whitespace_after',
                    semantic=semantic
                )
            )

            if isinstance(updated_node.operator, NotIn) or isinstance(updated_node.operator, IsNot):
                changed_node = changed_node.with_changes(
                    operator=self._remove_whitespace(
                        changed_node.operator,
                        'whitespace_between',
                        semantic=True
                    )
                )

            return changed_node

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
                    if (whitespace.first_line.comment is None and
                            all(map(lambda x: x.comment is None, whitespace.empty_lines))):
                        whitespace = SimpleWhitespace(value=' ' if semantic else '')
                    else:
                        if whitespace.first_line.comment is not None:
                            # keep trailing whitespace because of comment
                            whitespace = whitespace.with_deep_changes(
                                whitespace.first_line,
                                whitespace=SimpleWhitespace(
                                    value=''
                                ),
                                newline=Newline(
                                    value=None
                                )
                            )

                        whitespace = whitespace.with_changes(
                            indent=False,
                            empty_lines=[
                                line.with_changes(indent=False)
                                for line in whitespace.empty_lines
                                if line.comment is not None
                            ],
                            last_line=SimpleWhitespace(
                                value=' ' if semantic else ''
                            )
                        )
                elif MaybeSentinel.DEFAULT:
                    # do nothing
                    pass
                else:
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
            last_trailing_whitespace = None

            for statement in statements:
                if isinstance(statement, SimpleStatementLine):
                    if not all(map(lambda x: x.comment is None, statement.leading_lines)):
                        # need to merge previous lines because this statement contains leading comments
                        if len(collapse_queue) > 0:
                            updated_body.append(
                                cls._merge_statement_lines(
                                    lines=collapse_queue,
                                    leading_lines=leading_lines,
                                    trailing_whitespace=last_trailing_whitespace
                                )
                            )
                            collapse_queue.clear()
                            leading_lines.clear()

                        assert len(leading_lines) == 0

                        if statement.trailing_whitespace.comment is not None:
                            # can't collapse with following statement because of trailing whitespace
                            updated_body.append(
                                cls._merge_statement_lines(
                                    lines=[statement],
                                    leading_lines=statement.leading_lines,
                                    trailing_whitespace=statement.trailing_whitespace
                                )
                            )
                            collapse_queue.clear()
                            leading_lines.clear()
                        else:
                            # can possibly be merged with following lines
                            collapse_queue = [statement]
                            leading_lines = [*statement.leading_lines]
                            last_trailing_whitespace = statement.trailing_whitespace
                    elif statement.trailing_whitespace.comment is None:
                        # can possibly be merged with next lines
                        collapse_queue.append(statement)
                        leading_lines = [*statement.leading_lines]
                        last_trailing_whitespace = statement.trailing_whitespace
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
