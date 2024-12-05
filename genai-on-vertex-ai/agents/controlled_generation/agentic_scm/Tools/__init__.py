# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re
import ast
import importlib
from Tools.python_functions import *
from Tools.tool_instructions import return_tool_instruction, return_agent_instruction


__all__ = ["return_tool_instruction", "return_agent_instruction"]





def args_string_to_dict(args_string):
    args_dict = {}
    positional_arg_count = 0

    if args_string == '' or args_string == "":
        return None

    for arg in args_string.split(","):
        arg = arg.strip()
        if "=" in arg:
            key, value_str = arg.split("=")
            try:
                args_dict[key.strip()] = ast.literal_eval(value_str.strip())
            except (ValueError, SyntaxError):
                print(f"Warning: Could not parse argument: {arg}")
        else:
            # Directly append positional arguments to a list
            if "arg_list" not in args_dict:
                args_dict["arg_list"] = []
            args_dict["arg_list"].append(arg) 

    return args_dict


def run_function(function, function_name, function_args):
    try:
        args = args_string_to_dict(function_args)

        module_name = "Tools"
        module = importlib.import_module(module_name)
        function_to_call = getattr(module, function_name, None)

        if function_to_call:
            try:
                if args == None: 
                    result = function_to_call()
                # If there are positional arguments, unpack them
                elif "arg_list" in args:
                    result = function_to_call(*args["arg_list"]) 
                else:
                    result = function_to_call(**args)
                return result

            except (SyntaxError, NameError, ValueError) as e:
                return f"Error parsing arguments: {e}"
        else:
            return f"Function '{function_name}' not found in module '{module_name}'."

    except ImportError:
        return f"Module '{module_name}' not found."



    


