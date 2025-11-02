"""
Dynamic Function Executor

A Python client for interacting with the Nuclio Dynamic Function Executor.
Provides a convenient interface for executing Python functions remotely.
"""

import requests
import json
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """Result of a function execution"""
    success: bool
    result: Any = None
    stdout: str = ""
    stderr: str = ""
    function_name: str = ""
    params: Dict[str, Any] = None
    error: Optional[str] = None
    status_code: int = 200


class DynamicFunctionExecutor:
    """Client for the Nuclio Dynamic Function Executor"""

    def __init__(self, base_url: str = "http://localhost:8082"):
        """
        Initialize the executor client

        Args:
            base_url: Base URL of the function executor service
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def execute(
        self,
        function_code: str,
        params: Dict[str, Any],
        function_name: Optional[str] = None,
        timeout: int = 30
    ) -> ExecutionResult:
        """
        Execute a Python function remotely

        Args:
            function_code: Python function code as string
            params: Parameters to pass to the function
            function_name: Name of the function (optional)
            timeout: Request timeout in seconds

        Returns:
            ExecutionResult with the function output or error information
        """
        request_data = {
            "function": function_code,
            "params": params
        }

        if function_name:
            request_data["function_name"] = function_name

        try:
            response = self.session.post(
                self.base_url,
                json=request_data,
                timeout=timeout
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return ExecutionResult(
                        success=True,
                        result=data['data']['result'],
                        stdout=data['data']['stdout'],
                        stderr=data['data']['stderr'],
                        function_name=data['data']['function_name'],
                        params=data['data']['params']
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        error=data.get('error', 'Unknown function error'),
                        status_code=response.status_code
                    )
            else:
                try:
                    error_data = response.json()
                    return ExecutionResult(
                        success=False,
                        error=error_data.get('error', f'HTTP {response.status_code}'),
                        status_code=response.status_code
                    )
                except json.JSONDecodeError:
                    return ExecutionResult(
                        success=False,
                        error=f'HTTP {response.status_code}: {response.text}',
                        status_code=response.status_code
                    )

        except requests.exceptions.Timeout:
            return ExecutionResult(
                success=False,
                error="Function execution timed out"
            )
        except requests.exceptions.ConnectionError:
            return ExecutionResult(
                success=False,
                error="Cannot connect to function executor. Make sure it's running and the port is forwarded."
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )

    def test_connection(self) -> bool:
        """Test if the function executor is accessible"""
        try:
            result = self.execute(
                "def test(): return 'connection test successful'",
                {}
            )
            return result.success
        except Exception:
            return False

    def __call__(self, function_code: str, params: Dict[str, Any], **kwargs) -> ExecutionResult:
        """Convenience method to execute functions"""
        return self.execute(function_code, params, **kwargs)


# Convenience functions for common operations
def quick_execute(function_code: str, params: Dict[str, Any]) -> ExecutionResult:
    """
    Quick function execution with default settings

    Args:
        function_code: Python function code
        params: Function parameters

    Returns:
        ExecutionResult
    """
    executor = DynamicFunctionExecutor()
    return executor.execute(function_code, params)


def safe_execute(function_code: str, params: Dict[str, Any]) -> tuple[Any, Optional[str]]:
    """
    Execute function and return (result, error) tuple

    Args:
        function_code: Python function code
        params: Function parameters

    Returns:
        Tuple of (result, error) where one will be None
    """
    result = quick_execute(function_code, params)
    if result.success:
        return result.result, None
    else:
        return None, result.error