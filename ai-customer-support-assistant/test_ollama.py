import requests
import json

# Test Ollama connection
try:
    # Check if Ollama is running
    response = requests.get("http://localhost:11434")
    print("✅ Ollama is running!")
    
    # Test Mistral model
    print("\nTesting Mistral model...")
    
    payload = {
        "model": "mistral",
        "prompt": "Hello! Please respond with a simple greeting.",
        "stream": False
    }
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Mistral model response:", result.get("response", "No response"))
    else:
        print("❌ Error:", response.status_code, response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to Ollama. Make sure it's running with: ollama serve")
except Exception as e:
    print("❌ Error:", str(e))