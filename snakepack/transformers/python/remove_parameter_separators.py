from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, Parameters, ParamSlash, MaybeSentinel, ParamStar

from snakepack.transformers.python._base import PythonModuleTransformer, BatchablePythonModuleTransformer


class RemoveParameterSeparatorsTransformer(BatchablePythonModuleTransformer):
    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def leave_Parameters(self, original_node: Parameters, updated_node: Parameters) -> Parameters:
            updated_params = []
            updated_kwonly_params = original_node.kwonly_params
            updated_star_arg = original_node.star_arg

            if isinstance(original_node.posonly_ind, ParamSlash):
                #  convert positional-only parameters to normal parameters
                updated_params = [*original_node.posonly_params]

            updated_params.extend(original_node.params)

            if isinstance(original_node.star_arg, ParamStar) and all(map(lambda x: x.default is None, updated_params)):
                #  convert keyword-only parameters to normal parameters if no defaults are used
                kwonly_params_default_seen = False
                remove_param_star = True

                for param in updated_node.kwonly_params:
                    if param.default is not None:
                        kwonly_params_default_seen = True
                    elif kwonly_params_default_seen:
                        # keyword only parameter without default following after one with default
                        # this means we cannot remove the param star
                        remove_param_star = False

                if remove_param_star:
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