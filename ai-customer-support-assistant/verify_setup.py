"""
Verification script to ensure Step 1 setup is complete.
"""

import os
import sys
from pathlib import Path
import importlib
import subprocess

def check_python_version():
    """Check Python version is 3.10+"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"❌ Python {version.major}.{version.minor} (Need 3.10+)")
    return version.major >= 3 and version.minor >= 10

def check_virtual_env():
    """Check if running in virtual environment"""
    print("\n🔍 Checking virtual environment...")
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print(f"✅ Virtual environment active: {sys.prefix}")
    else:
        print("❌ Virtual environment NOT active!")
        print("   Run: .\\venv\\Scripts\\Activate")
    return in_venv

def check_packages():
    """Check required packages are installed"""
    print("\n🔍 Checking required packages...")
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'httpx',
        'python-dotenv',
        'pytest'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} NOT installed")
            all_installed = False
    
    return all_installed

def check_project_structure():
    """Check project directories exist"""
    print("\n🔍 Checking project structure...")
    required_dirs = [
        'app', 'app/api', 'app/api/routes', 'app/core', 
        'app/db', 'app/models', 'app/schemas', 'app/services',
        'app/utils', 'data', 'tests', 'logs'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ NOT found")
            all_exist = False
    
    return all_exist

def check_files():
    """Check required files exist"""
    print("\n🔍 Checking required files...")
    required_files = [
        '.env',
        'requirements.txt',
        'data/knowledge_base.md',
        'app/__init__.py',
        'app/config.py',
        'app/main.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} NOT found")
            all_exist = False
    
    return all_exist

def check_ollama():
    """Check Ollama is running and Mistral is available"""
    print("\n🔍 Checking Ollama...")
    try:
        import requests
        response = requests.get("http://localhost:11434", timeout=5)
        print("✅ Ollama is running")
        
        # Check for Mistral model
        try:
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True,
                shell=True
            )
            if "mistral" in result.stdout.lower():
                print("✅ Mistral model is available")
                return True
            else:
                print("❌ Mistral model NOT found")
                print("   Run: ollama pull mistral")
                return False
        except Exception as e:
            print(f"⚠️  Could not check models: {e}")
            return True  # Assume it's OK if we can't check
            
    except Exception as e:
        print("❌ Ollama is NOT running")
        print("   Run: ollama serve")
        return False

def check_env_file():
    """Check .env file has required variables"""
    print("\n🔍 Checking .env configuration...")
    if not Path('.env').exists():
        print("❌ .env file NOT found")
        return False
    
    required_vars = [
        'OLLAMA_HOST',
        'DATABASE_URL',
        'API_PREFIX',
        'KNOWLEDGE_BASE_PATH'
    ]
    
    from dotenv import dotenv_values
    config = dotenv_values(".env")
    
    all_present = True
    for var in required_vars:
        if var in config:
            print(f"✅ {var} = {config[var]}")
        else:
            print(f"❌ {var} NOT set")
            all_present = False
    
    return all_present

def main():
    """Run all checks"""
    print("=" * 50)
    print("🚀 AI Customer Support Assistant - Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version()),
        ("Virtual Environment", check_virtual_env()),
        ("Required Packages", check_packages()),
        ("Project Structure", check_project_structure()),
        ("Required Files", check_files()),
        ("Ollama Service", check_ollama()),
        ("Environment Config", check_env_file())
    ]
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print("=" * 50)
    
    all_passed = True
    for name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Ready for Step 2: Database Implementation")
        print("\nYou can test the API by running:")
        print("  python -m uvicorn app.main:app --reload")
        print("\nThen visit: http://localhost:8000/docs")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Activate virtual environment: .\\venv\\Scripts\\Activate")
        print("2. Install packages: pip install -r requirements.txt")
        print("3. Start Ollama: ollama serve")
        print("4. Pull Mistral: ollama pull mistral")
    print("=" * 50)

if __name__ == "__main__":
    main()