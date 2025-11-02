"""
Dynamic Python Function Executor
A Nuclio function that can execute arbitrary Python functions provided in requests
"""

import json
import sys
import traceback
import ast
import types
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

def handler(context, event):
    """
    Execute a Python function provided in the request body

    Expected JSON format:
    {
        "function": "def my_function(x, y): return x + y",
        "params": {"x": 5, "y": 10},
        "function_name": "my_function"  # optional, will use first function if not provided
    }
    """
    try:
        # Parse request body
        if event.body is None:
            return _error_response("No request body provided", 400, context)

        try:
            if isinstance(event.body, bytes):
                data = json.loads(event.body.decode('utf-8'))
            else:
                data = json.loads(event.body)
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as e:
            return _error_response(f"Invalid JSON in request body: {str(e)}", 400, context)

        # Validate required fields
        if 'function' not in data:
            return _error_response("Missing 'function' field in request", 400, context)

        if 'params' not in data:
            return _error_response("Missing 'params' field in request", 400, context)

        function_code = data['function']
        params = data['params']
        function_name = data.get('function_name', None)

        context.logger.info_with('Executing dynamic function',
                                function_name=function_name,
                                param_count=len(params))

        # Execute the function
        result = _execute_function(function_code, params, function_name, context)

        return _success_response(result, context)

    except Exception as e:
        context.logger.error_with('Unexpected error in handler',
                                 error=str(e),
                                 traceback=traceback.format_exc())
        return _error_response(f"Internal server error: {str(e)}", 500, context)


def _execute_function(function_code, params, function_name=None, context=None):
    """
    Execute a Python function from code string with given parameters
    """
    # Security: Basic code validation
    if not _is_safe_code(function_code):
        raise ValueError("Code contains potentially unsafe operations")

    # Create a namespace for the function
    namespace = {}

    try:
        # Parse and compile the function
        parsed = ast.parse(function_code, mode='exec')

        # Find function definitions
        function_defs = [node for node in parsed.body if isinstance(node, ast.FunctionDef)]

        if not function_defs:
            raise ValueError("No function definition found in provided code")

        # Use provided function name or find the first function
        if function_name:
            target_function = function_name
            # Verify the function exists
            if not any(f.name == function_name for f in function_defs):
                raise ValueError(f"Function '{function_name}' not found in code")
        else:
            # Use the first function definition
            target_function = function_defs[0].name
            function_name = target_function

        # Execute the code to define the function
        exec(compile(parsed, filename="<string>", mode="exec"), namespace)

        # Get the function
        if target_function not in namespace:
            raise ValueError(f"Function '{target_function}' not defined after execution")

        func = namespace[target_function]

        # Capture stdout and stderr
        stdout_capture = StringIO()
        stderr_capture = StringIO()

        # Execute the function with parameters
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            result = func(**params)

        # Get captured output
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()

        execution_info = {
            'function_name': function_name,
            'result': result,
            'stdout': stdout_output,
            'stderr': stderr_output,
            'params': params
        }

        if context:
            context.logger.info_with('Function executed successfully',
                                   function_name=function_name,
                                   result_type=type(result).__name__,
                                   has_stdout=bool(stdout_output),
                                   has_stderr=bool(stderr_output))

        return execution_info

    except SyntaxError as e:
        raise ValueError(f"Syntax error in function code: {str(e)}")
    except TypeError as e:
        raise ValueError(f"Parameter type error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Function execution error: {str(e)}")


def _is_safe_code(code):
    """
    Basic safety check for provided Python code
    """
    try:
        parsed = ast.parse(code, mode='exec')

        # Disallowed operations
        disallowed_nodes = (
            ast.Import,          # import statements
            ast.ImportFrom,      # from ... import
            ast.ClassDef,        # class definitions
            ast.AsyncFunctionDef, # async function definitions
        )

        disallowed_names = {
            'exec', 'eval', 'compile', '__import__', 'open', 'file',
            'input', 'raw_input', 'reload', 'vars', 'globals', 'locals',
            'dir', 'hasattr', 'getattr', 'setattr', 'delattr',
            'exit', 'quit', 'help', 'copyright', 'credits', 'license'
        }

        # Check for disallowed nodes
        for node in ast.walk(parsed):
            if isinstance(node, disallowed_nodes):
                return False

            # Check for disallowed names
            if isinstance(node, ast.Name) and node.id in disallowed_names:
                return False

            # Check for attribute access that might be dangerous
            if isinstance(node, ast.Attribute):
                # Disallow access to __builtins__, __file__, etc.
                if node.attr.startswith('__') and node.attr.endswith('__'):
                    return False

        return True

    except SyntaxError:
        return False


def _success_response(data, context):
    """Create a successful response"""
    response_data = {
        'status': 'success',
        'data': data
    }

    return context.Response(
        body=json.dumps(response_data, indent=2, default=str),
        headers={
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        content_type='application/json',
        status_code=200
    )


def _error_response(message, status_code=400, context=None):
    """Create an error response"""
    response_data = {
        'status': 'error',
        'error': message,
        'status_code': status_code
    }

    return context.Response(
        body=json.dumps(response_data, indent=2),
        headers={
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        content_type='application/json',
        status_code=status_code
    )