# Nuclio Function Sandbox - Agent Integration Guide

## 🎯 **Overview for Agentic Systems**

This document provides essential information for AI agents to interact with the Nuclio Dynamic Function Executor as a sandboxed execution environment.

## 🏗️ **Current Architecture**

### **System Components**
- **Platform**: Nuclio serverless framework on Kubernetes (Rancher Desktop + K3s)
- **Function Executor**: Dynamic Python function execution service
- **Security Model**: AST-based code validation with operation restrictions
- **Registry**: Local Docker registry (localhost:5000) for fast development

### **Access Information**
- **Function Executor URL**: `http://localhost:8082`
- **API Method**: `POST` requests only
- **Content-Type**: `application/json`
- **Response Format**: JSON with success/error status
- **Port Forward Command**: `kubectl port-forward -n nuclio svc/nuclio-function-executor 8082:8080`

### **⚠️ Port Forward Management**
**Critical**: The function executor requires port forwarding to be active. Redeployments create new pods that break existing port forwards.

#### **Port Forward Setup**
```bash
# Start port forward (run in separate terminal)
kubectl port-forward -n nuclio svc/nuclio-function-executor 8082:8080

# Or run in background
kubectl port-forward -n nuclio svc/nuclio-function-executor 8082:8080 &
```

#### **Troubleshooting Port Forward Issues**
If connection fails, run these diagnostic commands:
```bash
# Check if function pod is running
kubectl get pods -n nuclio | grep function-executor

# Check if service exists
kubectl get svc -n nuclio | grep function-executor

# Check function status
~/bin/nuctl get function function-executor --namespace nuclio

# Restart pod if needed
kubectl delete pod -n nuclio -l nuclio.io/function=function-executor
# Wait for new pod to be "Running", then restart port forward

# Kill all existing port forwards
pkill -f "kubectl port-forward.*nuclio-function-executor"

# Restart port forward
kubectl port-forward -n nuclio svc/nuclio-function-executor 8082:8080 &
```

## 📡 **API Specification**

### **Request Format**
```json
{
    "function": "def my_function(param1, param2): return param1 + param2",
    "params": {
        "param1": "value1",
        "param2": "value2"
    },
    "function_name": "my_function"  // optional, auto-detected
}
```

### **Response Format (Success)**
```json
{
    "status": "success",
    "data": {
        "function_name": "my_function",
        "result": "combined result",
        "stdout": "captured print statements",
        "stderr": "error output if any",
        "params": {"param1": "value1", "param2": "value2"}
    }
}
```

### **Response Format (Error)**
```json
{
    "status": "error",
    "error": "Description of what went wrong",
    "status_code": 400 or 500
}
```

## 🔒 **Security Constraints & Capabilities**

### **✅ ALLOWED Operations**
- Mathematical operations (+, -, *, /, %, **)
- String operations (concatenation, formatting, methods)
- List/dict comprehensions and manipulations
- Conditional logic (if/elif/else, ternary operators)
- Loop constructs (for, while)
- Function definitions and calls
- Print statements (captured in stdout)
- Basic data types (int, float, str, list, dict, tuple, set)

### **❌ BLOCKED Operations**
- Import statements (`import`, `from ... import`)
- File operations (`open`, `file`, read/write)
- Network operations (`requests`, `urllib`, sockets)
- System calls (`os`, `sys`, `subprocess`)
- Execution functions (`exec`, `eval`, `compile`)
- Database connections
- External API calls
- Class definitions
- Async/await syntax
- Decorators
- Global variable access

### **🛡️ Security Features**
- **AST Validation**: Code parsed and analyzed before execution
- **Operation Filtering**: Dangerous operations blocked at AST level
- **Parameter Validation**: Function parameters checked for type compatibility
- **Execution Time Limits**: Enforced by Nuclio platform
- **Memory Constraints**: Limited by container resources
- **Sandboxed Execution**: Isolated container environment

## 🧪 **Usage Patterns for Agents**

### **1. Basic Function Execution**
```python
# Agent prepares function code
function_code = """
def calculate_area(length, width):
    return length * width
"""

# Agent prepares parameters
parameters = {"length": 10, "width": 5}

# Agent makes HTTP request
response = requests.post("http://localhost:8082",
    json={"function": function_code, "params": parameters})
```

### **2. Data Processing Pattern**
```python
# Agent creates data transformation function
function_code = """
def process_sales_data(sales_records):
    total = sum(record['amount'] for record in sales_records)
    average = total / len(sales_records)
    return {
        'total_sales': total,
        'average_sale': average,
        'transaction_count': len(sales_records)
    }
"""

# Agent provides real data
parameters = {
    "sales_records": [
        {"id": 1, "amount": 100.50},
        {"id": 2, "amount": 75.25},
        {"id": 3, "amount": 150.00}
    ]
}
```

### **3. String Manipulation Pattern**
```python
# Agent creates text processing function
function_code = """
def analyze_text(text):
    words = text.lower().split()
    return {
        'word_count': len(words),
        'character_count': len(text),
        'words': words[:10]  # First 10 words
    }
"""

parameters = {"text": "The quick brown fox jumps over the lazy dog"}
```

### **4. Mathematical Computation Pattern**
```python
# Agent creates calculation function
function_code = """
def fibonacci_sequence(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]

    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[-1] + sequence[-2])
    return sequence
"""

parameters = {"n": 10}
```

## ⚡ **Performance Considerations**

### **Execution Speed**
- **Simple Functions**: < 50ms
- **Data Processing**: 100-500ms depending on data size
- **Complex Calculations**: 200-1000ms
- **Large Lists**: Performance degrades above 10,000 items

### **Memory Limits**
- **Function Memory**: Limited by Nuclio container (default ~512MB)
- **Parameter Size**: Keep JSON under 1MB for reliability
- **Result Size**: Large results may be truncated

### **Best Practices for Agents**
1. **Keep Functions Small**: Single-purpose functions work best
2. **Validate Parameters**: Check data before sending to sandbox
3. **Handle Errors**: Always check response status field
4. **Use Structured Data**: Pass complex data as dictionaries/lists
5. **Avoid Recursion Depth**: Keep recursion under 100 levels
6. **Print Debugging**: Use print statements for debugging (captured in stdout)

## 🔧 **Integration Guidelines**

### **Error Handling Pattern**
```python
def execute_safely(function_code, parameters):
    try:
        response = requests.post("http://localhost:8082",
            json={"function": function_code, "params": parameters},
            timeout=30)

        result = response.json()

        if result["status"] == "success":
            return result["data"]["result"], None
        else:
            return None, result["error"]

    except requests.exceptions.Timeout:
        return None, "Function execution timed out"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to function executor"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"
```

### **Function Validation Pattern**
```python
def validate_function_for_sandbox(function_code):
    # Check for blocked operations
    blocked_keywords = [
        'import', 'open(', 'file(', 'exec(', 'eval(', 'compile(',
        'os.', 'sys.', 'subprocess', 'requests', 'socket'
    ]

    for keyword in blocked_keywords:
        if keyword in function_code:
            return False, f"Blocked keyword detected: {keyword}"

    # Check function structure
    if 'def ' not in function_code:
        return False, "No function definition found"

    return True, "Function is sandbox-safe"
```

### **Response Parsing Pattern**
```python
def parse_sandbox_response(response):
    if response["status"] == "success":
        return {
            "success": True,
            "result": response["data"]["result"],
            "stdout": response["data"]["stdout"],
            "stderr": response["data"]["stderr"],
            "function_name": response["data"]["function_name"],
            "execution_info": {
                "parameters": response["data"]["params"],
                "output_captured": bool(response["data"]["stdout"])
            }
        }
    else:
        return {
            "success": False,
            "error": response["error"],
            "error_code": response.get("status_code"),
            "execution_failed": True
        }
```

## 🎯 **Recommended Agent Workflows**

### **1. Data Analysis Workflow**
1. Agent receives data processing request
2. Agent validates input data
3. Agent creates appropriate Python function
4. Agent validates function for sandbox safety
5. Agent executes function via sandbox API
6. Agent processes results and provides insights
7. Agent handles any errors gracefully

### **2. Calculation Workflow**
1. Agent identifies calculation requirements
2. Agent breaks complex calculation into smaller functions
3. Agent executes functions with appropriate parameters
4. Agent aggregates results from multiple executions
5. Agent presents final calculation results

### **3. Text Processing Workflow**
1. Agent analyzes text processing needs
2. Agent creates text manipulation functions
3. Agent processes text in chunks if needed
4. Agent combines results for comprehensive analysis

## 📊 **Current Capabilities Summary**

### **✅ What Agents Can Do**
- Execute mathematical calculations
- Process and transform data structures
- Manipulate strings and text
- Create algorithms and logic
- Debug with print statements
- Work with lists, dictionaries, and complex data
- Implement business logic
- Perform data analysis on structured data

### **❌ What Agents Cannot Do**
- Access external APIs or databases
- Read/write files
- Access network resources
- Use external libraries
- Execute system commands
- Perform long-running operations (>30 seconds)
- Access machine learning models
- Process very large datasets (>10MB)

## 🚀 **Quick Start for Agents**

```python
import requests

def execute_in_sandbox(function_code, parameters):
    """Execute Python code in Nuclio sandbox"""
    response = requests.post(
        "http://localhost:8082",
        json={"function": function_code, "params": parameters},
        headers={"Content-Type": "application/json"}
    )

    return response.json()

# Example usage
result = execute_in_sandbox(
    "def add_numbers(a, b): return a + b",
    {"a": 10, "b": 20}
)

if result["status"] == "success":
    print(f"Result: {result['data']['result']}")
else:
    print(f"Error: {result['error']}")
```

---

**Status**: ✅ **Sandbox ready for agent integration**
**Version**: 1.0.0
**Last Updated**: November 2, 2025

This document provides the essential knowledge needed for agentic systems to effectively use the Nuclio Dynamic Function Executor as a sandboxed Python execution environment.