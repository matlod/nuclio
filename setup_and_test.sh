#!/bin/bash

# Nuclio Development Workspace Setup and Test Script
# This script helps complete the setup process

set -e

echo "🚀 Nuclio Development Workspace Setup & Test"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check if we're in the right directory
    if [[ ! -f "SETUP_NOTES.md" ]]; then
        print_error "SETUP_NOTES.md not found. Make sure you're in the right directory."
        exit 1
    fi

    # Check if git is configured
    if ! git config --global user.name >/dev/null; then
        print_error "Git user.name not configured. Run: git config --global user.name 'Your Name'"
        exit 1
    fi

    print_status "Prerequisites check passed!"
}

# GitHub fork instructions
github_fork_instructions() {
    print_warning "Manual step required: Fork the repository on GitHub"
    echo ""
    echo "Please follow these steps:"
    echo "1. Open https://github.com/nuclio/nuclio in your browser"
    echo "2. Click the 'Fork' button in the top right"
    echo "3. Select your GitHub account (matlod)"
    echo "4. Wait for the fork to be created"
    echo ""
    echo "Once your fork is created, run: ./setup_and_test.sh --post-fork"
    echo ""
    exit 0
}

# Post-fork setup
post_fork_setup() {
    print_status "Setting up git remotes after fork..."

    # Remove old remote if exists
    git remote remove matlod 2>/dev/null || true

    # Add your fork
    git remote add matlod https://github.com/matlod/nuclio.git

    # Push to your fork
    print_status "Pushing to your fork..."
    git push matlod dynamic-function-experiments

    print_status "✅ Successfully pushed to your fork!"
    echo "Your repository is available at: https://github.com/matlod/nuclio"
}

# Check Nuclio status
check_nuclio_status() {
    print_status "Checking Nuclio installation..."

    # Check if function executor is running
    if curl -s http://localhost:8082 >/dev/null 2>&1; then
        print_status "✅ Function executor is accessible on port 8082"
    else
        print_warning "Function executor not accessible. Make sure port-forward is running:"
        echo "  kubectl port-forward -n nuclio svc/nuclio-function-executor 8082:8080 &"
    fi

    # Check if dashboard is running
    if curl -s http://localhost:8070 >/dev/null 2>&1; then
        print_status "✅ Nuclio dashboard is accessible on port 8070"
    else
        print_warning "Nuclio dashboard not accessible. Make sure port-forward is running:"
        echo "  kubectl port-forward -n nuclio svc/nuclio-dashboard 8070:8070 &"
    fi
}

# Test the function executor
test_function_executor() {
    print_status "Testing Dynamic Function Executor..."

    # Simple test
    echo "Testing simple math function..."
    response=$(curl -s -X POST http://localhost:8082 \
        -H "Content-Type: application/json" \
        -d '{"function": "def add(a, b): return a + b", "params": {"a": 5, "b": 7}}')

    if echo "$response" | grep -q '"status": "success"'; then
        print_status "✅ Basic function test passed!"
    else
        print_error "Basic function test failed"
        echo "Response: $response"
    fi

    # Run comprehensive test suite
    if [[ -f "test_function_executor.py" ]]; then
        print_status "Running comprehensive test suite..."
        if python3 test_function_executor.py; then
            print_status "✅ All tests passed!"
        else
            print_error "Some tests failed"
        fi
    fi
}

# Show access information
show_access_info() {
    print_status "Access Information:"
    echo ""
    echo "📊 Nuclio Dashboard: http://localhost:8070"
    echo "🔧 Function Executor: http://localhost:8082"
    echo "🧪 Test Function: http://localhost:8081 (if running)"
    echo ""
    echo "📚 Documentation:"
    echo "  - Complete Setup: SETUP_NOTES.md"
    echo "  - Function Executor: FUNCTION_EXECUTOR.md"
    echo "  - Workspace Guide: README_WORKSPACE.md"
    echo ""
    echo "🛠️  Quick Test Examples:"
    echo "  # Math function"
    echo "  curl -X POST http://localhost:8082 \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"function\": \"def add(a, b): return a + b\", \"params\": {\"a\": 10, \"b\": 20}}'"
    echo ""
    echo "  # String processing"
    echo "  curl -X POST http://localhost:8082 \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"function\": \"def hello(name): return f\\\"Hello {name}!\\\"\", \"params\": {\"name\": \"World\"}}'"
}

# Main script logic
main() {
    case "${1:-}" in
        "--post-fork")
            post_fork_setup
            check_nuclio_status
            test_function_executor
            show_access_info
            ;;
        "--test-only")
            check_nuclio_status
            test_function_executor
            ;;
        "--help"|"-h")
            echo "Usage: $0 [option]"
            echo ""
            echo "Options:"
            echo "  (no args)    Run complete setup (includes fork instructions)"
            echo "  --post-fork  Setup after you've created the fork on GitHub"
            echo "  --test-only  Only test existing installation"
            echo "  --help, -h   Show this help message"
            ;;
        *)
            check_prerequisites
            github_fork_instructions
            ;;
    esac
}

# Run main function with all arguments
main "$@"