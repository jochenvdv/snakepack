from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, FunctionDef, SimpleStatementSuite, IndentedBlock, Pass, BaseSmallStatement, Expr, Integer, BaseSuite, \
    BaseNumber, BaseString, Tuple, BaseList, BaseSet, BaseDict

from snakepack.analyzers.python.literals import LiteralDuplicationAnalyzer
from snakepack.transformers.python._base import PythonModuleTransformer, BatchablePythonModuleTransformer


class RemoveLiteralStatementsTransformer(BatchablePythonModuleTransformer):
    REQUIRED_ANALYZERS = PythonModuleTransformer.REQUIRED_ANALYZERS + [
        LiteralDuplicationAnalyzer
    ]

    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def leave_SimpleStatementSuite(
                self,
                original_node: SimpleStatementSuite,
                updated_node: SimpleStatementSuite,
        ) -> BaseSuite:
            if len(updated_node.body) > 1:
                return updated_node.with_changes(
                    body=[
                        stmt
                        for stmt in updated_node.body
                        if (not isinstance(stmt, Expr) or
                            (stmt.value is not Ellipsis and
                            not isinstance(stmt.value, (
                                    BaseNumber,
                                    BaseString,
                                    Tuple,
                                    BaseList,
                                    BaseSet,
                                    BaseDict
                                )
                            ))
                        )
                    ]
                )

            return updated_node

        def leave_IndentedBlock(self, original_node: IndentedBlock, updated_node: IndentedBlock) -> BaseSuite:
            changed_body = []

            for line in updated_node.body:
                if isinstance(line, SimpleStatementLine):
                    changed_line = line.with_changes(
                        body=[
                            stmt
                            for stmt in line.body
                            if not isinstance(stmt, Expr) or
                                (stmt.value is not Ellipsis and
                                    not isinstance(stmt.value, (
                                            BaseNumber,
                                            BaseString,
                                            Tuple,
                                            BaseList,
                                            BaseSet,
                                            BaseDict
                                    )
                                )
                            )
                        ]
                    )

                    if len(changed_line.body) > 0:
                        changed_body.append(changed_line)
                else:
                    changed_body.append(line)




            if len(changed_body) == 0:
                # statement required - add 0 literal
                changed_body.append(
                    SimpleStatementLine(
                        body=[
                            Expr(
                                value=Integer(
                                    value='0'
                                )
                            )
                        ]
                    )
                )

            return updated_node.with_changes(body=changed_body)

    __config_name__ = 'remove_literal_statements'
