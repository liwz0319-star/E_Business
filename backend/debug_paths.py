import requests

paths = [
    "http://localhost:8000/ws/socket.io/?EIO=4&transport=polling",
    "http://localhost:8000/socket.io/?EIO=4&transport=polling",
    "http://localhost:8000/ws/?EIO=4&transport=polling",
    "http://localhost:8000/api/v1/copywriting/generate" # Check API too
]

with open("debug_output.txt", "w") as f:
    for url in paths:
        try:
            f.write(f"Testing {url}...\n")
            resp = requests.get(url)
            f.write(f"Status: {resp.status_code}\n")
            f.write(f"Content: {resp.text[:200]}\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
        f.write("-" * 20 + "\n")
