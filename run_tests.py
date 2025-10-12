#!/usr/bin/env python3
"""
Test runner script for portfolio website.
Provides easy commands to run different test suites.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print("""
🚀 Portfolio Website Test Runner

Usage: python run_tests.py <command>

Available commands:
  all          - Run all tests
  unit         - Run unit tests only
  api          - Run API tests only
  integration  - Run integration tests only
  ml           - Run ML-specific tests only
  fast         - Run fast tests (excludes slow tests)
  coverage     - Run tests with coverage report
  install      - Install test dependencies
  help         - Show this help message

Examples:
  python run_tests.py all
  python run_tests.py unit
  python run_tests.py coverage
        """)
        return

    command = sys.argv[1].lower()
    
    # Change to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    if command == 'help':
        main()
        return
    
    elif command == 'install':
        print("📦 Installing test dependencies...")
        success = run_command(
            "pip install -r requirements.txt",
            "Installing requirements"
        )
        if success:
            print("✅ Test dependencies installed successfully!")
        else:
            print("❌ Failed to install dependencies")
        return
    
    elif command == 'all':
        success = run_command(
            "python -m pytest tests/ -v",
            "Running all tests"
        )
        
    elif command == 'unit':
        success = run_command(
            "python -m pytest tests/test_unit.py -v -m unit",
            "Running unit tests"
        )
        
    elif command == 'api':
        success = run_command(
            "python -m pytest tests/test_api.py -v -m api",
            "Running API tests"
        )
        
    elif command == 'integration':
        success = run_command(
            "python -m pytest tests/test_integration.py -v -m integration",
            "Running integration tests"
        )
        
    elif command == 'ml':
        success = run_command(
            "python -m pytest tests/ -v -m ml",
            "Running ML-specific tests"
        )
        
    elif command == 'fast':
        success = run_command(
            "python -m pytest tests/ -v -m 'not slow'",
            "Running fast tests (excluding slow tests)"
        )
        
    elif command == 'coverage':
        print("📊 Installing coverage tool...")
        subprocess.run("pip install coverage", shell=True, check=False)
        
        success1 = run_command(
            "coverage run -m pytest tests/ -v",
            "Running tests with coverage tracking"
        )
        
        if success1:
            success2 = run_command(
                "coverage report -m",
                "Generating coverage report"
            )
            
            run_command(
                "coverage html",
                "Generating HTML coverage report"
            )
            
            if success2:
                print("\n📈 Coverage report generated!")
                print("📄 Text report shown above")
                print("🌐 HTML report: htmlcov/index.html")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python run_tests.py help' for available commands")
        return
    
    # Print summary
    if 'success' in locals():
        if success:
            print(f"\n✅ {command.upper()} tests completed successfully!")
        else:
            print(f"\n❌ {command.upper()} tests failed!")
            sys.exit(1)

if __name__ == "__main__":
    main()
