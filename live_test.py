"""Live HTTP test against running Flask server."""
import urllib.request, json

base = 'http://127.0.0.1:5000'

def post_json(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data,
          headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def get_json(url):
    req = urllib.request.Request(url, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

results = []

# Health check
code, data = get_json(base + '/api/health')
ok = code == 200 and data.get('success')
results.append(('Health check', code, ok, data.get('message', '')))

# Student login with registration number (primary flow)
code, data = post_json(base + '/auth/login', {'identifier': 'CS/2026/0001', 'password': 'student123'})
ok = code == 200 and data.get('success')
results.append(('Student login (reg#)', code, ok, data.get('message', '')))

# Student login with email (secondary flow - David Wilson has no reg number)
code, data = post_json(base + '/auth/login', {'identifier': 'david.wilson@student.edu', 'password': 'student123'})
ok = code == 200 and data.get('success')
results.append(('Student login (email, no reg#)', code, ok, data.get('message', '')))

# Admin login
code, data = post_json(base + '/auth/login', {'identifier': 'admin@university.edu', 'password': 'admin123'})
ok = code == 200 and data.get('success')
results.append(('Admin login', code, ok, data.get('message', '')))

# Registrar login
code, data = post_json(base + '/auth/login', {'identifier': 'registrar@university.edu', 'password': 'admin123'})
ok = code == 200 and data.get('success')
results.append(('Registrar login', code, ok, data.get('message', '')))

# Wrong password
code, data = post_json(base + '/auth/login', {'identifier': 'CS/2026/0001', 'password': 'wrongpass'})
ok = code == 401 and not data.get('success')
results.append(('Wrong password rejected', code, ok, data.get('message', '')))

# Wrong identifier
code, data = post_json(base + '/auth/login', {'identifier': 'nobody@example.com', 'password': 'test'})
ok = code == 401 and not data.get('success')
results.append(('Unknown user rejected', code, ok, data.get('message', '')))

# Registration
code, data = post_json(base + '/auth/register', {
    'name': 'Test Student', 'email': 'testregister@student.edu',
    'phone': '+254700000001', 'password': 'testpass123'
})
ok = code == 201 and data.get('success')
results.append(('Registration', code, ok, data.get('message', '')))

print()
print("=" * 65)
print("LIVE HTTP TEST RESULTS")
print("=" * 65)
all_pass = True
for name, code, ok, msg in results:
    status = "PASS" if ok else "FAIL"
    if not ok:
        all_pass = False
    print(f"  [{status}] {name}")
    print(f"         HTTP {code} | {msg}")
print("=" * 65)
print("OVERALL:", "ALL PASS" if all_pass else "SOME FAILED")
