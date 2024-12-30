import subprocess
import requests

def test_http_connection():
    url = "https://www.google.com"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"HTTP Connection Successful: {response.status_code}")
        else:
            print(f"HTTP Connection Failed: {response.status_code}")
    except Exception as e:
        print(f"HTTP Connection Test Error: {e}")

def test_ping():
    host = "8.8.8.8"  # Google DNS
    try:
        result = subprocess.run(["adb", "shell", "ping", "-c", "4", host], capture_output=True, text=True)
        if "0% packet loss" in result.stdout:
            print("Ping Test Successful")
        else:
            print("Ping Test Failed")
        print(result.stdout)
    except Exception as e:
        print(f"Ping Test Error: {e}")

if __name__ == "__main__":
    print("Starting HTTP and Ping tests...")
    # test_http_connection()
    test_ping()