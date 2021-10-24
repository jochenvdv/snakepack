from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, Parameters, ParamSlash, MaybeSentinel, ParamStar

from snakepack.transformers.python._base import PythonModuleCstTransformer


class RemoveParameterSeparatorsTransformer(PythonModuleCstTransformer):
    class _CstTransformer(CSTTransformer):
        def leave_Parameters(self, original_node: Parameters, updated_node: Parameters) -> Parameters:
            updated_params = []
            updated_kwonly_params = original_node.kwonly_params
            updated_star_arg = original_node.star_arg

            if isinstance(original_node.posonly_ind, ParamSlash):
                #  convert positional-only parameters to normal parameters
                updated_params = [*original_node.posonly_params]

            updated_params.extend(original_node.params)

            if isinstance(original_node.star_arg, ParamStar):
                #  convert keyword-only parameters to normal parameters
                updated_star_arg = MaybeSentinel.DEFAULT
                updated_kwonly_params = []
                updated_params.extend(original_node.kwonly_params)

            return updated_node.with_changes(
                posonly_params=[],
                posonly_ind=MaybeSentinel.DEFAULT,
                params=updated_params,
                star_arg=updated_star_arg,
                kwonly_params=updated_kwonly_params,
                star_kwarg=original_node.star_kwarg
            )


    __config_name__ = 'remove_parameter_separators'