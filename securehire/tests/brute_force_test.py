import requests, time

URL = 'http://localhost:8000/api/v1/auth/login'
TARGET = 'applicant@test.com'

for i in range(15):
    resp = requests.post(URL, data={
        'username': TARGET,
        'password': f'wrongpass{i}'
    })
    print(f'Attempt {i+1}: HTTP {resp.status_code} — {resp.text[:100]}')
    time.sleep(0.3)
