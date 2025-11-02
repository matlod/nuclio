# Nuclio Development Workspace

This is a customized development workspace for experimenting with [Nuclio](https://nuclio.io/), the high-performance serverless platform for real-time events and data processing.

## 🚀 What's Included

### Core Infrastructure
- **Nuclio Platform**: Complete local serverless setup with Rancher Desktop + K3s
- **Local Registry**: Docker registry on port 5000 for fast local development
- **Dynamic Function Executor**: Execute arbitrary Python functions at runtime
- **Comprehensive Documentation**: Setup guides and infrastructure lessons learned

### Development Tools
- **uv**: Modern Python package manager
- **Pre-configured Tooling**: Black, Ruff, MyPy, PyTest
- **Test Suite**: Comprehensive function executor tests
- **Project Structure**: Organized workspace for experiments

## 📋 Prerequisites

### System Requirements
- **Docker**: Required for Rancher Desktop
- **Rancher Desktop**: Running with K3s enabled
- **Python 3.12+**: For local development
- **uv**: Python package manager (auto-installed)
- **kubectl**: Kubernetes CLI
- **nuctl**: Nuclio CLI tool

### Quick Setup Check
```bash
# Check if Rancher Desktop is running
docker version

# Check if Kubernetes is available
kubectl cluster-info

# Check if Nuclio is installed
nuctl version
```

## 🛠️ Installation

### 1. Install uv (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/snap/code/205/.local/share/../bin/env
```

### 2. Set up the Python environment
```bash
# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate

# Install dependencies
uv sync --dev
```

### 3. Set up Nuclio Platform
Follow the detailed setup instructions in [`SETUP_NOTES.md`](SETUP_NOTES.md)

## 🧪 Testing the Dynamic Function Executor

### Start Required Services
```bash
# Start Nuclio Dashboard port forward
kubectl port-forward -n nuclio svc/nuclio-dashboard 8070:8070 &

# Start Function Executor port forward
kubectl port-forward -n nuclio svc/nuclio-function-executor 8082:8080 &
```

### Run the Test Suite
```bash
# Make test executable
chmod +x test_function_executor.py

# Run comprehensive tests
./test_function_executor.py
```

### Manual Testing Examples

#### Simple Math Function
```bash
curl -X POST http://localhost:8082 \
    -H "Content-Type: application/json" \
    -d '{
        "function": "def add_numbers(a, b): return a + b",
        "params": {"a": 10, "b": 25}
    }'
```

#### String Processing
```bash
curl -X POST http://localhost:8082 \
    -H "Content-Type: application/json" \
    -d '{
        "function": "def process_text(text, prefix): return f\"{prefix}: {text.upper()}\"",
        "params": {"text": "hello world", "prefix": "RESULT"}
    }'
```

#### List Manipulation
```bash
curl -X POST http://localhost:8082 \
    -H "Content-Type: application/json" \
    -d '{
        "function": "def filter_even(numbers): return [n for n in numbers if n % 2 == 0]",
        "params": {"numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    }'
```

## 📁 Project Structure

```
nuclio/
├── README_WORKSPACE.md          # This file
├── SETUP_NOTES.md               # Complete setup guide
├── FUNCTION_EXECUTOR.md        # Dynamic function executor docs
├── pyproject.toml              # Python project configuration
├── function_executor.py        # Dynamic function executor code
├── test_function_executor.py   # Comprehensive test suite
├── .venv/                      # Python virtual environment
└── docs/                       # Original Nuclio documentation
```

## 🔧 Development Workflow

### 1. Creating New Functions
```python
# Create function in function_executor.py or separate files
def my_custom_function(param1, param2):
    # Your function logic here
    return result
```

### 2. Testing Functions
```bash
# Use the test suite
./test_function_executor.py

# Or test manually with curl
curl -X POST http://localhost:8082 -H "Content-Type: application/json" \
    -d '{"function": "def test(): return \"Hello World\"", "params": {}}'
```

### 3. Code Quality
```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type checking
uv run mypy .

# Run tests
uv run pytest
```

## 🌐 Access Points

### Nuclio Dashboard
- **URL**: http://localhost:8070
- **Purpose**: Visual function management
- **Port Forward**: 8070

### Dynamic Function Executor
- **URL**: http://localhost:8082
- **Purpose**: Execute Python functions via API
- **Port Forward**: 8082

### Test Function (Hello World)
- **URL**: http://localhost:8081
- **Purpose**: Basic function testing
- **Port Forward**: 8081

## 🔒 Security Features

The Dynamic Function Executor includes several security measures:

- **No File System Access**: Functions cannot read/write files
- **No Import Statements**: Cannot import external libraries
- **No Network Operations**: Cannot make network requests
- **No System Commands**: Cannot execute shell commands
- **AST Validation**: Code is parsed and validated before execution

## 📊 Monitoring

### Check Function Status
```bash
# List all functions
nuctl get function --namespace nuclio

# Check function details
nuctl get function function-executor --namespace nuclio

# View logs
kubectl logs -n nuclio -l nuclio.io/function=function-executor -f
```

### Check System Resources
```bash
# Check pod status
kubectl get pods --namespace nuclio

# Check local registry
curl -s http://localhost:5000/v2/_catalog
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Forward Issues**
   ```bash
   # Kill existing port forwards
   pkill -f "kubectl port-forward"

   # Restart port forwards
   kubectl port-forward -n nuclio svc/nuclio-dashboard 8070:8070 &
   ```

2. **Registry Issues**
   ```bash
   # Check if local registry is running
   docker ps | grep local-registry

   # Restart registry if needed
   docker restart local-registry
   ```

3. **Function Deployment Issues**
   ```bash
   # Check Nuclio controller logs
   kubectl logs -n nuclio -l app=nuclio-controller -f

   # Redeploy function
   nuctl deploy function-executor --namespace nuclio --path function_executor.py --runtime python:3.12 --handler function_executor:handler --registry localhost:5000 --run-registry localhost:5000
   ```

## 🚀 Next Steps

### Ideas for Experiments
1. **Data Processing Functions**: Create functions for data transformation
2. **API Integration**: Build functions that call external APIs (when allowed)
3. **Machine Learning**: Experiment with ML model inference
4. **Web Scraping**: Parse and process web data
5. **Image Processing**: Manipulate image data (if image libraries allowed)

### Production Considerations
1. **Security Review**: Implement proper authentication and authorization
2. **Monitoring**: Add comprehensive logging and metrics
3. **Resource Limits**: Configure appropriate memory and CPU limits
4. **Scaling**: Test auto-scaling behavior
5. **CI/CD**: Set up automated testing and deployment

## 📚 Additional Resources

- [Nuclio Official Documentation](https://docs.nuclio.io/)
- [Nuclio GitHub Repository](https://github.com/nuclio/nuclio)
- [Rancher Desktop](https://rancherdesktop.io/)
- [uv Python Package Manager](https://docs.astral.sh/uv/)

---

**Happy Serverless Development! 🚀**

This workspace provides everything you need to experiment with Nuclio and serverless functions in a safe, local environment.