
import requests
try:
    url = 'http://localhost:5001/static/uploads/690b3a3fbd6cec019d53b008_1764889449_Screenshot_2025-11-26_144402.png'
    r = requests.head(url)
    print(f"Status: {r.status_code}")
    print(f"CORS Origin: {r.headers.get('Access-Control-Allow-Origin')}")
    print(f"All Headers: {r.headers}")
except Exception as e:
    print(f"Error: {e}")
