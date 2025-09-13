import requests
import json
import time

def test_api():
    base_url = "http://localhost:5000"
    
    print("Testing Catan Map Maker API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test basic map generation
    try:
        response = requests.get(f"{base_url}/generate")
        if response.status_code == 200:
            data = response.json()
            print(f"Basic generation: Success")
            print(f"Number of tiles: {len([t for t in data['map']['tiles'] if t is not None])}")
        else:
            print(f"Basic generation failed: {response.status_code}")
    except Exception as e:
        print(f"Basic generation error: {e}")
    
    # Test no-pairs generation
    try:
        response = requests.get(f"{base_url}/generate-no-pairs")
        if response.status_code == 200:
            data = response.json()
            print(f"No-pairs generation: Success")
            print(f"Pairs avoided: {data['pairs_avoided']}")
        else:
            print(f"No-pairs generation failed: {response.status_code}")
    except Exception as e:
        print(f"No-pairs generation error: {e}")

if __name__ == "__main__":
    test_api()
