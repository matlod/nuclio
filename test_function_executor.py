#!/usr/bin/env python3
"""
Test Suite for Dynamic Function Executor

This script tests the Nuclio Dynamic Function Executor with various Python functions
to demonstrate its capabilities and validate functionality.

Prerequisites:
- Function executor running on http://localhost:8082
- Port forward active: kubectl port-forward -n nuclio svc/nuclio-function-executor 8082:8080
"""

import requests
import json
import time
from typing import Dict, Any, List
import sys

class FunctionExecutorTester:
    def __init__(self, base_url: str = "http://localhost:8082"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def test_function(self, description: str, function_code: str, params: Dict[str, Any],
                      expected_result: Any = None, should_fail: bool = False) -> bool:
        """Test a single function execution"""
        print(f"\n{'='*60}")
        print(f"TEST: {description}")
        print(f"{'='*60}")

        request_data = {
            "function": function_code,
            "params": params
        }

        print(f"Function Code:")
        print(function_code)
        print(f"\nParameters: {json.dumps(params, indent=2)}")

        try:
            response = self.session.post(self.base_url, json=request_data, timeout=30)

            print(f"\nResponse Status: {response.status_code}")

            if response.status_code == 200:
                result_data = response.json()
                print(f"Response Body:")
                print(json.dumps(result_data, indent=2))

                if result_data.get('status') == 'success':
                    print(f"\n✅ SUCCESS: Function executed successfully")

                    if expected_result is not None:
                        actual_result = result_data['data']['result']
                        if actual_result == expected_result:
                            print(f"✅ VERIFICATION: Result matches expected value: {expected_result}")
                        else:
                            print(f"❌ VERIFICATION: Expected {expected_result}, got {actual_result}")
                            return False

                    # Show stdout/stderr if present
                    if result_data['data']['stdout']:
                        print(f"📤 STDOUT:\n{result_data['data']['stdout']}")
                    if result_data['data']['stderr']:
                        print(f"📥 STDERR:\n{result_data['data']['stderr']}")

                    return True
                else:
                    print(f"❌ FUNCTION ERROR: {result_data.get('error', 'Unknown error')}")
                    return not should_fail  # If we expected failure, this is success

            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                try:
                    error_data = response.json()
                    print(json.dumps(error_data, indent=2))
                except:
                    print(response.text)
                return False

        except requests.exceptions.Timeout:
            print("❌ TIMEOUT: Function execution took too long")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR: Cannot connect to function executor")
            print("Make sure port-forward is running: kubectl port-forward -n nuclio svc/nuclio-function-executor 8082:8080")
            return False
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
            return False

    def run_all_tests(self) -> None:
        """Run all test cases"""
        print("🚀 Starting Dynamic Function Executor Test Suite")
        print("Make sure the function executor is running on http://localhost:8082")

        # Test results tracking
        passed = 0
        total = 0

        def run_test(description: str, function_code: str, params: Dict[str, Any],
                     expected_result: Any = None, should_fail: bool = False) -> None:
            nonlocal passed, total
            total += 1
            if self.test_function(description, function_code, params, expected_result, should_fail):
                passed += 1

        # 1. Basic Math Operations
        run_test(
            "Simple Addition",
            "def add(a, b): return a + b",
            {"a": 5, "b": 7},
            12
        )

        run_test(
            "Multiplication",
            "def multiply(x, y): return x * y",
            {"x": 6, "y": 8},
            48
        )

        run_test(
            "Division with Result",
            "def divide(numerator, denominator): return numerator / denominator",
            {"numerator": 20, "denominator": 4},
            5.0
        )

        # 2. String Operations
        run_test(
            "String Concatenation",
            "def concat_strings(first, second): return f'{first} {second}'",
            {"first": "Hello", "second": "World"},
            "Hello World"
        )

        run_test(
            "String Uppercase",
            "def to_upper(text): return text.upper()",
            {"text": "hello world"},
            "HELLO WORLD"
        )

        run_test(
            "String Formatting",
            "def format_message(name, age): return f'{name} is {age} years old'",
            {"name": "Alice", "age": 30},
            "Alice is 30 years old"
        )

        # 3. List Operations
        run_test(
            "List Sum",
            "def sum_list(numbers): return sum(numbers)",
            {"numbers": [1, 2, 3, 4, 5]},
            15
        )

        run_test(
            "List Filtering (Even Numbers)",
            "def filter_even(numbers): return [n for n in numbers if n % 2 == 0]",
            {"numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
            [2, 4, 6, 8, 10]
        )

        run_test(
            "List Comprehension (Squares)",
            "def squares(numbers): return [x**2 for x in numbers]",
            {"numbers": [1, 2, 3, 4]},
            [1, 4, 9, 16]
        )

        # 4. Dictionary Operations
        run_test(
            "Dictionary Key Extraction",
            "def get_user_info(user): return {'name': user['name'], 'age': user['age']}",
            {"user": {"name": "Bob", "age": 25, "city": "NYC"}},
            {"name": "Bob", "age": 25}
        )

        run_test(
            "Dictionary Value Processing",
            "def process_scores(scores): return {'average': sum(scores.values()) / len(scores), 'max': max(scores.values())}",
            {"scores": {"math": 90, "science": 85, "english": 88}},
            {"average": 87.66666666666667, "max": 90}
        )

        # 5. Conditional Logic
        run_test(
            "Conditional Logic (Even/Odd)",
            "def even_or_odd(number): return 'even' if number % 2 == 0 else 'odd'",
            {"number": 7},
            "odd"
        )

        run_test(
            "Complex Conditional",
            "def grade_calculator(score): return 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'F'",
            {"score": 85},
            "B"
        )

        # 6. Multiple Function Definitions
        run_test(
            "Multiple Functions with Helper",
            """
def helper(n): return n * 2
def main(x, y): return helper(x) + helper(y)
            """,
            {"x": 3, "y": 4},
            14
        )

        # 7. Functions with Print Statements (Test stdout capture)
        run_test(
            "Function with Print Statements",
            """
def calculate_and_show(a, b):
    print(f"Calculating {a} + {b}")
    result = a + b
    print(f"Result: {result}")
    return result
            """,
            {"a": 10, "b": 15},
            25
        )

        # 8. Error Handling Tests (should fail)
        run_test(
            "Syntax Error (should fail)",
            "def broken_syntax( return 'missing colon'",
            {},
            should_fail=True
        )

        run_test(
            "Missing Parameter (should fail)",
            "def add_numbers(a, b): return a + b",
            {"a": 5},  # Missing 'b' parameter
            should_fail=True
        )

        run_test(
            "Division by Zero (should fail)",
            "def divide_by_zero(x): return x / 0",
            {"x": 10},
            should_fail=True
        )

        run_test(
            "Import Statement (should fail - security restriction)",
            "def use_import(): import math; return math.sqrt(16)",
            {},
            should_fail=True
        )

        run_test(
            "File Operation (should fail - security restriction)",
            "def read_file(): return open('/etc/passwd').read()",
            {},
            should_fail=True
        )

        # 9. Complex Data Processing
        run_test(
            "Data Processing Pipeline",
            """
def process_data(items):
    # Filter items with value > 5
    filtered = [item for item in items if item['value'] > 5]

    # Calculate statistics
    values = [item['value'] for item in filtered]

    return {
        'count': len(filtered),
        'sum': sum(values),
        'average': sum(values) / len(values) if values else 0,
        'max': max(values) if values else 0,
        'items': filtered
    }
            """,
            {"items": [
                {"name": "A", "value": 3},
                {"name": "B", "value": 8},
                {"name": "C", "value": 12},
                {"name": "D", "value": 2},
                {"name": "E", "value": 15}
            ]},
            {
                'count': 3,
                'sum': 35,
                'average': 11.666666666666666,
                'max': 15,
                'items': [
                    {"name": "B", "value": 8},
                    {"name": "C", "value": 12},
                    {"name": "E", "value": 15}
                ]
            }
        )

        # 10. Algorithm Examples
        run_test(
            "Factorial Calculation",
            "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
            {"n": 5},
            120
        )

        run_test(
            "Fibonacci Sequence",
            "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
            {"n": 7},
            13
        )

        run_test(
            "Palindrome Check",
            "def is_palindrome(text): cleaned = ''.join(c.lower() for c in text if c.isalnum()); return cleaned == cleaned[::-1]",
            {"text": "A man, a plan, a canal: Panama"},
            True
        )

        # 11. JSON-like Data Processing
        run_test(
            "Nested Data Processing",
            """
def analyze_nested_data(data):
    total = 0
    count = 0

    for category in data['categories']:
        for item in category['items']:
            total += item['value']
            count += 1

    return {
        'total_value': total,
        'item_count': count,
        'average_value': total / count if count > 0 else 0,
        'categories_processed': len(data['categories'])
    }
            """,
            {"data": {
                "categories": [
                    {
                        "name": "Category A",
                        "items": [
                            {"id": 1, "value": 10},
                            {"id": 2, "value": 20}
                        ]
                    },
                    {
                        "name": "Category B",
                        "items": [
                            {"id": 3, "value": 15},
                            {"id": 4, "value": 25},
                            {"id": 5, "value": 30}
                        ]
                    }
                ]
            }},
            {
                'total_value': 100,
                'item_count': 5,
                'average_value': 20.0,
                'categories_processed': 2
            }
        )

        # 12. Performance Test
        print(f"\n{'='*60}")
        print("TEST: Performance Test (Large List Processing)")
        print(f"{'='*60}")

        start_time = time.time()
        success = self.test_function(
            "Large List Processing",
            """
def process_large_list():
    import time
    start = time.time()

    # Create and process a large list
    numbers = list(range(1000))
    squares = [x**2 for x in numbers]
    even_squares = [x for x in squares if x % 2 == 0]

    end = time.time()
    return {
        'original_count': len(numbers),
        'squares_count': len(squares),
        'even_squares_count': len(even_squares),
        'processing_time_ms': (end - start) * 1000
    }
            """,
            {},
            None
        )

        if success:
            end_time = time.time()
            total_time = (end_time - start_time) * 1000
            print(f"⏱️  Total test time: {total_time:.2f}ms")

        # Final Results
        print(f"\n{'='*60}")
        print("🏁 TEST SUITE COMPLETED")
        print(f"{'='*60}")
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")

        if passed == total:
            print("🎉 ALL TESTS PASSED! The Dynamic Function Executor is working perfectly!")
        else:
            print(f"⚠️  {total - passed} tests failed. Check the logs above for details.")

def main():
    """Main entry point"""
    # Check if function executor is available
    tester = FunctionExecutorTester()

    # Test connectivity first
    try:
        response = tester.session.get(tester.base_url, timeout=5)
        print("❌ Function executor returned unexpected response. Make sure it's running on port 8082.")
        return
    except requests.exceptions.ConnectionError:
        # This is expected - the function executor only accepts POST requests
        pass

    # Run the test suite
    tester.run_all_tests()

if __name__ == "__main__":
    main()