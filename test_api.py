import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:8000"

# Register
patient_data = {
    "first_name": "Ali",
    "last_name": "Valiyev",
    "phone_number": "+998901234567",
    "password": "strongpassword"
}
req = urllib.request.Request(f"{base_url}/api/auth/register", data=json.dumps(patient_data).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as response:
        print("Register:", response.getcode(), response.read().decode())
except urllib.error.HTTPError as e:
    print("Register Error:", e.code, e.read().decode())

# Login
login_data = urllib.parse.urlencode({
    "username": "+998901234567",
    "password": "strongpassword"
}).encode('utf-8')
req2 = urllib.request.Request(f"{base_url}/api/auth/login", data=login_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
try:
    with urllib.request.urlopen(req2) as response:
        res_data = json.loads(response.read().decode())
        print("Login:", response.getcode(), res_data)
        token = res_data.get("access_token")
        
        # Get Me
        req3 = urllib.request.Request(f"{base_url}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req3) as r3:
            print("Get Me:", r3.getcode(), r3.read().decode())
except urllib.error.HTTPError as e:
    print("Login Error:", e.code, e.read().decode())
