
<<<<<<< HEAD
# SecureHire Lab Project
=======
# SecureHire-
Secure Software Design &amp; Development Final project- CYC386
>>>>>>> 0fc337edf24e5292cf75b16ff196b2b91ba584


# SecureHire — Complete Testing Guide
### CYC386 Secure Software Design | Demo: June 12, 2026 | COMSATS University Islamabad

> **Your project structure:** `SecureHire-main/securehire/` — all commands run from this root unless noted.

---

## TABLE OF CONTENTS
1. [Initial Setup & File Structure](#1-initial-setup--file-structure)
2. [Docker Testing — Full Commands](#2-docker-testing--full-commands)
3. [Kubernetes Testing — Full Commands](#3-kubernetes-testing--full-commands)
4. [Application Functional Testing](#4-application-functional-testing)
5. [RED TEAM — Attack Playbook](#5-red-team--attack-playbook)
6. [BLUE TEAM — Defense & Monitoring](#6-blue-team--defense--monitoring)
7. [Automated Security Scanning](#7-automated-security-scanning)
8. [Demo Day Checklist](#8-demo-day-checklist)

---

## 1. Initial Setup & File Structure

```
SecureHire-main/
└── securehire/
    ├── src/
    │   ├── backend/          ← FastAPI Python app
    │   │   ├── api/v1/       ← auth, jobs, applications routers
    │   │   ├── auth/         ← JWT handler, dependencies
    │   │   ├── cache/        ← Redis client
    │   │   ├── kafka/        ← Kafka producer
    │   │   ├── middleware/   ← SQL injection, XSS, security headers
    │   │   ├── logs/         ← securehire.log, anomalies.log
    │   │   ├── main.py
    │   │   └── .env
    │   └── frontend/         ← React + Vite app
    ├── docker/
    │   ├── Dockerfile.backend
    │   ├── Dockerfile.frontend
    │   └── docker-compose.yml
    ├── k8s/
    │   └── securehire.yaml
    ├── monitor/
    │   ├── prometheus/prometheus.yml
    │   └── falco/securehire_rules.yaml
    ├── ci/github-actions.yml
    ├── iac/main.tf
    ├── docs/policy.rego
    └── setup.sh
```

### One-Time Setup
```bash
# Navigate to project root
cd SecureHire-main/securehire

# Run the automated setup script first
chmod +x setup.sh
./setup.sh

# Or manually install Python deps (for local testing without Docker)
pip install -r src/backend/requirements.txt
```

---

## 2. Docker Testing — Full Commands

### 2.1 Build & Start All Services

```bash
# Navigate to the docker folder OR use -f flag
cd SecureHire-main/securehire

# BUILD all images from scratch (use this first time or after code changes)
docker compose -f docker/docker-compose.yml build --no-cache

# Start all containers in detached mode
docker compose -f docker/docker-compose.yml up -d

# Start with live logs visible (good for demo)
docker compose -f docker/docker-compose.yml up

# Quick shortcut if you're inside the docker/ folder
cd docker/
docker compose up -d
```

### 2.2 Verify All Containers Are Running

```bash
# List all running containers with status and ports
docker ps

# You should see these containers:
# securehire-backend    → 0.0.0.0:8000->8000/tcp
# securehire-frontend   → 0.0.0.0:5173->5173/tcp
# securehire-postgres   → 5432/tcp  (NOT exposed to host — good!)
# securehire-redis      → 6379/tcp  (NOT exposed to host — good!)
# securehire-kafka      → 9092/tcp
# securehire-zookeeper  → 2181/tcp
# prometheus            → 0.0.0.0:9090->9090/tcp
# grafana               → 0.0.0.0:3000->3000/tcp
```

### 2.3 Docker Security Tests (CIS Benchmark Checks)

```bash
# ─── TEST 1: Check if containers run as non-root (CRITICAL) ───
docker inspect securehire-backend --format '{{.Config.User}}'
# EXPECTED: 'appuser' or a non-empty string
# BAD:      empty string = running as root = FAIL

# ─── TEST 2: Verify read-only root filesystem ───
docker inspect securehire-backend --format '{{.HostConfig.ReadonlyRootfs}}'
# EXPECTED: true

# ─── TEST 3: No privileged mode ───
docker inspect securehire-backend --format '{{.HostConfig.Privileged}}'
# EXPECTED: false

# ─── TEST 4: Check memory limits are set ───
docker inspect securehire-backend --format '{{.HostConfig.Memory}}'
# EXPECTED: non-zero number (e.g., 536870912 = 512MB)

# ─── TEST 5: Check CPU quota ───
docker inspect securehire-backend --format '{{.HostConfig.CpuQuota}}'
# EXPECTED: non-zero

# ─── TEST 6: List all port mappings ───
docker ps --format 'table {{.Names}}\t{{.Ports}}'
# Redis/Postgres should NOT show 0.0.0.0:xxxx (should be internal only)

# ─── TEST 7: Check network isolation ───
docker network ls
docker network inspect securehire_default
# All containers should be on the same internal network

# ─── TEST 8: Verify no secrets in environment variables ───
docker inspect securehire-backend --format '{{range .Config.Env}}{{println .}}{{end}}'
# Should show env vars but NOT raw passwords (should reference .env or secrets)

# ─── TEST 9: Check image layers for vulnerabilities ───
# Install Trivy first: https://aquasecurity.github.io/trivy/
trivy image Docker-backend:latest
trivy image Docker-frontend:latest
# Review HIGH and CRITICAL findings

# ─── TEST 10: Redis should require auth from host ───
redis-cli -h localhost -p 6379 ping
# EXPECTED: Connection refused OR NOAUTH error
# BAD: PONG (means Redis is open with no auth)
```

### 2.4 Docker Log Commands

```bash
# View backend logs (all)
docker logs securehire-backend

# Follow logs in real-time
docker logs -f securehire-backend

# Last 100 lines
docker logs --tail 100 securehire-backend

# Filter for security events only
docker logs -f securehire-backend 2>&1 | grep -i \
  'SQL injection\|XSS\|HIGH_RISK\|BURST\|locked\|unauthorized\|403\|429\|anomaly'

# View Kafka logs
docker logs securehire-kafka

# View all container logs at once
docker compose -f docker/docker-compose.yml logs -f
```

### 2.5 Docker Container Management

```bash
# Stop all services
docker compose -f docker/docker-compose.yml down

# Stop and remove volumes (RESETS DATABASE — use carefully)
docker compose -f docker/docker-compose.yml down -v

# Restart a single service
docker compose -f docker/docker-compose.yml restart backend

# Execute shell inside backend container
docker exec -it securehire-backend bash
docker exec -it securehire-backend sh    # if bash not available

# Copy files out of container (e.g., logs)
docker cp securehire-backend:/app/logs/anomalies.log ./reports/

# View container resource usage
docker stats

# Inspect full container config
docker inspect securehire-backend | python3 -m json.tool
```

### 2.6 Docker Image Analysis

```bash
# View image history / layers
docker history securehire-backend:latest

# Show image size
docker images | grep securehire

# Verify multi-stage build worked (image should be small)
# A proper multi-stage build should be < 200MB for the backend

# Check Dockerfile is using non-root user
cat docker/Dockerfile.backend | grep -i 'user\|adduser\|useradd'
# Should show: RUN adduser --system appuser && USER appuser

# Check no secrets in Dockerfile
cat docker/Dockerfile.backend | grep -i 'password\|secret\|key\|token'
# Should return nothing — secrets go in .env, not Dockerfile
```

---

## 3. Kubernetes Testing — Full Commands

### 3.1 Prerequisites

```bash
# Install kubectl (if not installed)
# Ubuntu/Debian:
sudo apt-get update && sudo apt-get install -y kubectl

# Verify kubectl is connected to a cluster
kubectl cluster-info

# For local testing, use Minikube or Kind:
# Minikube:
minikube start --driver=docker
minikube status

# Kind (Kubernetes in Docker):
kind create cluster --name securehire
kubectl cluster-info --context kind-securehire
```

### 3.2 Deploy SecureHire to Kubernetes

```bash
# Apply the main Kubernetes manifest
kubectl apply -f k8s/securehire.yaml

# Verify all resources were created
kubectl get all -n securehire
# OR if using default namespace:
kubectl get all

# Watch pods start up in real-time
kubectl get pods -w

# Expected pods:
# securehire-backend-xxxx    Running
# securehire-frontend-xxxx   Running
# postgres-xxxx              Running
# redis-xxxx                 Running
# kafka-xxxx                 Running
```

### 3.3 Kubernetes Security Tests

```bash
# ─── TEST 1: Check Pod Security Standards ───
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext}{"\n"}{end}'

# ─── TEST 2: Verify containers don't run as root ───
kubectl get pod -l app=securehire-backend -o jsonpath=\
'{.items[0].spec.containers[0].securityContext.runAsNonRoot}'
# EXPECTED: true

kubectl get pod -l app=securehire-backend -o jsonpath=\
'{.items[0].spec.containers[0].securityContext.runAsUser}'
# EXPECTED: non-zero number (e.g., 1000)

# ─── TEST 3: Check readOnlyRootFilesystem ───
kubectl get pod -l app=securehire-backend -o jsonpath=\
'{.items[0].spec.containers[0].securityContext.readOnlyRootFilesystem}'
# EXPECTED: true

# ─── TEST 4: Check privilege escalation is disabled ───
kubectl get pod -l app=securehire-backend -o jsonpath=\
'{.items[0].spec.containers[0].securityContext.allowPrivilegeEscalation}'
# EXPECTED: false

# ─── TEST 5: Check capabilities are dropped ───
kubectl get pod -l app=securehire-backend -o yaml | grep -A5 'capabilities'
# EXPECTED: drop: [ALL]

# ─── TEST 6: Verify Network Policies exist ───
kubectl get networkpolicies
kubectl describe networkpolicy

# ─── TEST 7: Check RBAC roles ───
kubectl get roles
kubectl get rolebindings
kubectl get clusterroles | grep securehire

# ─── TEST 8: Verify resource limits are set ───
kubectl get pod -l app=securehire-backend -o jsonpath=\
'{.items[0].spec.containers[0].resources}'
# EXPECTED: shows limits and requests for CPU and memory

# ─── TEST 9: Check service account permissions ───
kubectl get serviceaccounts
kubectl describe serviceaccount securehire-backend

# ─── TEST 10: Audit the full pod spec ───
kubectl get pod -l app=securehire-backend -o yaml
```

### 3.4 Kubernetes Operational Commands

```bash
# View pod logs
kubectl logs -l app=securehire-backend
kubectl logs -l app=securehire-backend -f    # follow

# View logs for a specific pod
kubectl logs securehire-backend-xxxx-yyyy

# Describe a pod (shows events, resource usage)
kubectl describe pod -l app=securehire-backend

# Execute into a pod
kubectl exec -it $(kubectl get pod -l app=securehire-backend -o name | head -1) -- bash

# Port-forward to access service locally (when no LoadBalancer)
kubectl port-forward service/securehire-backend 8000:8000
kubectl port-forward service/securehire-frontend 5173:5173

# Check service endpoints
kubectl get services
kubectl describe service securehire-backend

# Scale the deployment
kubectl scale deployment securehire-backend --replicas=3

# Rolling restart (after config change)
kubectl rollout restart deployment/securehire-backend
kubectl rollout status deployment/securehire-backend

# View ConfigMaps and Secrets
kubectl get configmaps
kubectl get secrets
kubectl describe secret securehire-secrets    # shows keys, NOT values

# Delete all resources (reset)
kubectl delete -f k8s/securehire.yaml
```

### 3.5 CIS Kubernetes Benchmark Checks

```bash
# Check API server flags (if you have cluster admin access)
kubectl get pod -n kube-system -l component=kube-apiserver -o yaml | \
  grep -E 'anonymous-auth|authorization-mode|audit-log'

# Check etcd encryption
kubectl get secret -o yaml | grep -i encryptionConfig

# List all pods running in kube-system (privileged namespace audit)
kubectl get pods -n kube-system

# Check for pods with host network access (security risk)
kubectl get pods --all-namespaces -o json | \
  python3 -c "import json,sys; pods=json.load(sys.stdin)['items']; \
  [print(p['metadata']['name']) for p in pods if p['spec'].get('hostNetwork')]"

# Verify no pods have hostPID
kubectl get pods --all-namespaces -o json | \
  python3 -c "import json,sys; pods=json.load(sys.stdin)['items']; \
  [print(p['metadata']['name']) for p in pods if p['spec'].get('hostPID')]"
```

---

## 4. Application Functional Testing

### 4.1 Health & Basic Connectivity

```bash
# Backend health check
curl http://localhost:8000/health
# EXPECTED: {"status": "healthy", "service": "SecureHire"}

# Prometheus metrics endpoint
curl http://localhost:8000/metrics
# EXPECTED: Prometheus-formatted metrics text

# Frontend
curl http://localhost:5173
# EXPECTED: HTML of React app

# OpenAPI spec (only in DEBUG mode)
curl http://localhost:8000/api/openapi.json | python3 -m json.tool
```

### 4.2 User Registration & Authentication Flow

```bash
# ─── REGISTER as applicant ───
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "applicant@test.com",
    "password": "Secure@123",
    "full_name": "Test Applicant",
    "role": "applicant"
  }'

# ─── REGISTER as employer ───
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "employer@test.com",
    "password": "Secure@123",
    "full_name": "Test Employer",
    "role": "employer"
  }'

# ─── REGISTER as admin ───
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "admin@test.com",
    "password": "Admin@123",
    "full_name": "Admin User",
    "role": "admin"
  }'

# ─── LOGIN and capture token ───
export APP_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d 'username=applicant@test.com&password=Secure@123' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $APP_TOKEN"

# ─── GET current user info ───
curl -H "Authorization: Bearer $APP_TOKEN" \
     http://localhost:8000/api/v1/auth/me

# ─── REFRESH token ───
export REFRESH_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d 'username=applicant@test.com&password=Secure@123' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['refresh_token'])")

curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H 'Content-Type: application/json' \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"

# ─── LOGOUT ───
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $APP_TOKEN"
```

### 4.3 Jobs API Testing

```bash
# Get employer token
export EMP_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d 'username=employer@test.com&password=Secure@123' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# ─── LIST public jobs (no auth needed) ───
curl http://localhost:8000/api/v1/jobs/

# ─── CREATE a job (employer only) ───
curl -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Authorization: Bearer $EMP_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Software Engineer",
    "company": "Tech Corp",
    "description": "Build amazing software",
    "location": "Remote",
    "salary": "100000"
  }'

# ─── GET a specific job ───
curl http://localhost:8000/api/v1/jobs/1

# ─── GET pending jobs (admin only) ───
export ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d 'username=admin@test.com&password=Admin@123' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     http://localhost:8000/api/v1/jobs/pending
```

### 4.4 Applications API Testing

```bash
# Applicant applies for a job
curl -X POST http://localhost:8000/api/v1/applications/ \
  -H "Authorization: Bearer $APP_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"job_id": 1, "cover_letter": "I am interested in this position."}'

# Employer views applications for their job
curl -H "Authorization: Bearer $EMP_TOKEN" \
     http://localhost:8000/api/v1/applications/
```

---

## 5. RED TEAM — Attack Playbook

> Run ALL red team tests against your LOCAL instance only. Document every finding.

### 5.1 Reconnaissance

```bash
# ─── Port scan ───
nmap -sV -p 1-10000 localhost
# Expected open: 8000, 5173, 9090, 3000
# Unexpected open: 5432 (Postgres), 6379 (Redis) = VULNERABILITY

# ─── Enumerate all API endpoints ───
curl http://localhost:8000/api/openapi.json | python3 -m json.tool
# Also visit: http://localhost:8000/api/docs (Swagger UI)

# ─── Check for information disclosure in headers ───
curl -I http://localhost:8000/health
# BAD if you see: Server: uvicorn, X-Powered-By, etc.
```

### 5.2 Authentication Attacks

#### TEST 1 — Brute Force / Rate Limiting
```bash
# Save as brute_force_test.py
cat > brute_force_test.py << 'EOF'
import requests, time

URL = 'http://localhost:8000/api/v1/auth/login'
TARGET = 'victim@test.com'

for i in range(15):
    resp = requests.post(URL, data={
        'username': TARGET,
        'password': f'wrongpass{i}'
    })
    print(f'Attempt {i+1}: HTTP {resp.status_code} — {resp.text[:100]}')
    time.sleep(0.3)
EOF
python3 brute_force_test.py
# EXPECTED: 401 for first 5, then 423 (locked), then 429 (rate limited)
```

#### TEST 2 — JWT Algorithm None Attack
```bash
# Step 1: Get valid token
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d 'username=applicant@test.com&password=Secure@123'

# Step 2: Create a fake 'alg:none' token
python3 -c "
import base64, json

header = base64.urlsafe_b64encode(
    json.dumps({'alg':'none','typ':'JWT'}).encode()
).rstrip(b'=').decode()

payload = base64.urlsafe_b64encode(
    json.dumps({'sub':'1','role':'admin','type':'access'}).encode()
).rstrip(b'=').decode()

fake_token = f'{header}.{payload}.'
print('Fake token:', fake_token)
"

# Step 3: Use the fake token
curl -H 'Authorization: Bearer PASTE_FAKE_TOKEN_HERE' \
     http://localhost:8000/api/v1/auth/me
# EXPECTED: HTTP 401 Unauthorized
```

#### TEST 3 — Privilege Escalation
```bash
# Register as applicant, get token
export ATK_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"attacker@evil.com","password":"Attack@123","full_name":"Red Tester","role":"applicant"}' \
  && curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d 'username=attacker@evil.com&password=Attack@123' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Try to access admin endpoint with applicant token
curl -H "Authorization: Bearer $ATK_TOKEN" \
     http://localhost:8000/api/v1/jobs/pending
# EXPECTED: HTTP 403 Forbidden

# Try to create a job as applicant (employer-only)
curl -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Authorization: Bearer $ATK_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Hacked Job","company":"Evil Corp","location":"Remote"}'
# EXPECTED: HTTP 403 Forbidden
```

### 5.3 Injection Attacks

#### TEST 4 — SQL Injection
```bash
# Test 1: SQLi in query parameter
curl 'http://localhost:8000/api/v1/jobs/?skip=0%20OR%201=1'
# EXPECTED: HTTP 400 'Invalid input detected'

# Test 2: Classic login bypass
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=' OR '1'='1' --&password=anything"
# EXPECTED: HTTP 401 or 400 (NOT a successful login)

# Test 3: UNION injection
curl "http://localhost:8000/api/v1/jobs/1%20UNION%20SELECT%201,2,3--"
# EXPECTED: HTTP 400

# Test 4: SQLi in registration body
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"sqli@test.com","password":"Test@123","full_name":"A'\'''; DROP TABLE users;--","role":"applicant"}'
# EXPECTED: HTTP 400 (blocked by middleware)

# Test 5: Automated SQLMap scan
sqlmap -u 'http://localhost:8000/api/v1/jobs/?skip=0' \
  --level=3 --risk=1 --batch \
  -H "Authorization: Bearer $APP_TOKEN"
```

#### TEST 5 — XSS
```bash
# XSS in job title
curl -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Authorization: Bearer $EMP_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "<script>alert(document.cookie)</script>",
    "company": "Test Corp",
    "description": "<img src=x onerror=alert(1)>",
    "location": "Remote"
  }'
# EXPECTED: HTTP 400 (blocked by XSSMiddleware)

# Reflected XSS in URL parameter
curl 'http://localhost:8000/api/v1/jobs/?q=<script>alert(1)</script>'
# EXPECTED: HTTP 400
```

#### TEST 6 — IDOR (Broken Object Level Authorization)
```bash
# Register TWO applicants
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user_a@test.com","password":"Secure@123","full_name":"User A","role":"applicant"}'

curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user_b@test.com","password":"Secure@123","full_name":"User B","role":"applicant"}'

# Get User A and User B tokens
export TOKEN_A=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d 'username=user_a@test.com&password=Secure@123' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

export TOKEN_B=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d 'username=user_b@test.com&password=Secure@123' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# User A applies for a job
curl -X POST http://localhost:8000/api/v1/applications/ \
  -H "Authorization: Bearer $TOKEN_A" \
  -H 'Content-Type: application/json' \
  -d '{"job_id": 1, "cover_letter": "User A application"}'

# User B tries to read User A's application (IDOR test)
curl -H "Authorization: Bearer $TOKEN_B" \
     http://localhost:8000/api/v1/applications/1
# EXPECTED: HTTP 403 or 404 (NOT User A's data)
```

### 5.4 Infrastructure & Security Header Tests

#### TEST 7 — Security Headers Check
```bash
# Check all required security headers
curl -I http://localhost:8000/health

# Required headers (verify ALL are present):
# ✓ X-Frame-Options: DENY
# ✓ X-Content-Type-Options: nosniff
# ✓ Strict-Transport-Security: max-age=31536000; includeSubDomains
# ✓ Content-Security-Policy: default-src 'self'...
# ✓ X-XSS-Protection: 1; mode=block
# ✓ Referrer-Policy: strict-origin-when-cross-origin

# ABSENT (information disclosure - should NOT appear):
# ✗ Server:
# ✗ X-Powered-By:
```

#### TEST 8 — Rate Limiting / DoS Simulation
```bash
# Install apache bench
sudo apt install apache2-utils   # Ubuntu
# brew install httpd             # Mac

# Send 100 rapid requests to health
ab -n 100 -c 10 http://localhost:8000/health

# Send 50 requests to login (triggers rate limiter after 10/min)
echo 'username=test@test.com&password=wrong' > /tmp/login.txt
ab -n 50 -c 5 -p /tmp/login.txt \
   -T 'application/x-www-form-urlencoded' \
   http://localhost:8000/api/v1/auth/login

# Check logs for rate limit triggers
docker logs securehire-backend 2>&1 | grep -i '429\|rate limit\|BURST'
```

#### TEST 9 — CSRF & SSRF
```bash
# CSRF test (no CSRF token required for JSON APIs, but check cookie flags)
curl -v -X POST http://localhost:8000/api/v1/auth/login \
  -d 'username=applicant@test.com&password=Secure@123' 2>&1 | grep -i 'set-cookie'
# EXPECTED: Cookie flags should show HttpOnly, SameSite=Strict

# SSRF test — try to make backend fetch internal resources
curl -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Authorization: Bearer $EMP_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Test","company":"Test","location":"Remote","description":"http://169.254.169.254/metadata"}'
# EXPECTED: Either 400 or no internal metadata in response
```

### 5.5 Red Team Findings Report Template

Save your findings using this format in `/reports/red_team_findings.md`:

```
FINDING #__ — [Name]
─────────────────────────────────────────────
Severity:     HIGH / MEDIUM / LOW / INFO
Endpoint:     POST /api/v1/auth/login
OWASP:        A07:2021 - Identification and Authentication Failures
MITRE ATT&CK: T1110.001 — Password Guessing
Description:  What you found and how
Steps:        1. Register user  2. Run brute_force_test.py  3. Observe HTTP 429
Evidence:     Screenshot / HTTP response code
Fix:          Implement stricter rate limiting / CAPTCHA
```

---

## 6. BLUE TEAM — Defense & Monitoring

### 6.1 Open These Windows Before Demo

```
Terminal 1  → docker logs -f securehire-backend 2>&1 | grep security events
Terminal 2  → tail -f src/backend/logs/anomalies.log
Terminal 3  → kubectl get pods -w  (if using K8s)
Browser 1   → http://localhost:9090  (Prometheus)
Browser 2   → http://localhost:3000  (Grafana — login: admin/admin123)
Browser 3   → http://localhost:5173  (SecureHire frontend)
```

### 6.2 Real-Time Monitoring Commands

```bash
# ─── Watch ALL security events live ───
docker logs -f securehire-backend 2>&1 | grep -i \
  'SQL injection\|XSS\|HIGH_RISK\|BURST\|locked\|unauthorized\|403\|429\|WARNING\|CRITICAL'

# ─── Watch anomaly detection file ───
tail -f src/backend/logs/anomalies.log
# You'll see: BURST_ATTACK, IP_SWITCHING, OFF_HOURS_LOGIN events

# ─── Watch failed login attempts ───
docker logs -f securehire-backend 2>&1 | grep -i 'Failed login\|locked\|429'

# ─── Count 429 responses (rate limit hits) ───
docker logs securehire-backend 2>&1 | grep '429' | wc -l

# ─── Count blocked SQL injection attempts ───
docker logs securehire-backend 2>&1 | grep -i 'SQL injection' | wc -l

# ─── Show X-Risk-Score in response headers ───
curl -v http://localhost:8000/health 2>&1 | grep -i 'risk'
```

### 6.3 Trigger & Demonstrate Anomaly Detection (LIVE DEMO)

```bash
# Terminal 1 — Watch anomaly log
tail -f src/backend/logs/anomalies.log

# Terminal 2 — Trigger BURST_ATTACK
python3 -c "
import requests, time
for i in range(25):
    r = requests.get('http://localhost:8000/health')
    score = r.headers.get('X-Risk-Score', '0')
    print(f'Request {i+1}: Risk Score = {score}')
    time.sleep(0.1)
"
# Watch Terminal 1 — you'll see: ANOMALY | BURST_ATTACK | IP: 127.0.0.1 | 21 reqs/60s

# Trigger IP_SWITCHING anomaly (login from multiple "IPs")
# This is done by running login from different terminals / network configs
```

### 6.4 Prometheus Queries (show in browser at localhost:9090)

```promql
# Total request rate
rate(http_requests_total[1m])

# 4xx error rate (shows attack attempts)
rate(http_requests_total{status=~"4.."}[1m])

# 429 Rate limit hits
rate(http_requests_total{status="429"}[1m])

# 403 Forbidden (authorization failures)
rate(http_requests_total{status="403"}[1m])

# Response latency 95th percentile
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Total blocked SQL injections
increase(http_requests_total{status="400"}[5m])
```

### 6.5 Falco — Runtime Security

```bash
# Check Falco is running
docker logs -f falco 2>&1 | grep -i 'WARNING\|CRITICAL\|NOTICE'

# Simulate suspicious shell execution (triggers Falco alert)
docker exec securehire-backend sh -c 'echo test'
# Falco will fire: "Shell spawned in container"

# Watch Falco alerts in real time
docker logs -f falco
```

### 6.6 Grafana Dashboard Setup

```bash
# Access Grafana: http://localhost:3000
# Login: admin / admin123

# Add Prometheus as data source:
# Configuration → Data Sources → Add → Prometheus
# URL: http://prometheus:9090
# Save & Test

# Create dashboard with these panels:
# Panel 1: Time series → rate(http_requests_total[1m])     → "Request Rate"
# Panel 2: Time series → rate(http_requests_total{status=~"4.."}[1m]) → "4xx Errors"
# Panel 3: Stat      → rate(http_requests_total{status="429"}[1m]) → "Rate Limit Hits"
# Panel 4: Time series → histogram_quantile(0.95, ...)     → "P95 Latency"
```

### 6.7 IBM QRadar — What to Explain to Examiner

```
SecureHire produces structured JSON logs. In QRadar:

1. Log Source: Configure QRadar to ingest SecureHire's JSON logs via Syslog/API
2. Custom Rules created:
   - IF event = "Failed login" AND same source IP AND count >= 5 within 60s
     → Create OFFENSE (severity: HIGH) → Alert security team
   - IF event = "SQL injection attempt" → Immediate OFFENSE
   - IF X-Risk-Score >= 60 → Flag for investigation
3. Falco alerts forwarded to QRadar via Syslog (container runtime events)
4. Dashboard shows: active offenses, top attacking IPs, event timeline

Sample JSON log SecureHire sends to QRadar:
{
  "timestamp": "2026-06-12T10:15:32Z",
  "level": "WARNING",
  "event": "SQL injection attempt detected",
  "ip": "192.168.1.100",
  "path": "/api/v1/jobs/",
  "risk_score": 75
}
```

---

## 7. Automated Security Scanning

### 7.1 OWASP ZAP

```bash
# Option A: GUI (recommended for demo)
# 1. Open OWASP ZAP
# 2. Automated Scan → URL: http://localhost:8000
# 3. Click Attack → wait 10-15 minutes
# 4. Report → Generate Report → HTML
# 5. Save to: reports/zap-scan-report.html

# Option B: Command Line
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://host.docker.internal:8000 \
  -r zap-report.html

# Option C: Import OpenAPI spec for better coverage
# In ZAP: Import → OpenAPI from URL: http://localhost:8000/api/openapi.json
# Then Active Scan
```

### 7.2 SonarQube (SAST)

```bash
# Start SonarQube
docker run -d --name sonarqube -p 9001:9000 sonarqube:community

# Access: http://localhost:9001
# Default credentials: admin/admin

# Install sonar-scanner
pip install sonar-scanner   # or download from sonarqube.org

# Run scan on backend code
sonar-scanner \
  -Dsonar.projectKey=securehire \
  -Dsonar.sources=src/backend \
  -Dsonar.host.url=http://localhost:9001 \
  -Dsonar.login=YOUR_TOKEN

# View results: http://localhost:9001/dashboard?id=securehire
```

### 7.3 Trivy — Container Vulnerability Scanning

```bash
# Install Trivy
sudo apt install trivy   # Ubuntu
# brew install trivy     # Mac

# Scan backend image
trivy image securehire-backend:latest

# Scan and save report
trivy image --format json --output reports/trivy-backend.json \
  securehire-backend:latest

# Scan only HIGH/CRITICAL
trivy image --severity HIGH,CRITICAL securehire-backend:latest

# Scan frontend image
trivy image securehire-frontend:latest

# Scan filesystem (source code)
trivy fs src/backend/
```

### 7.4 CodeQL

```bash
# GitHub provides CodeQL via GitHub Actions (already in ci/github-actions.yml)
# To run locally:
pip install codeql   # or download CLI from GitHub

codeql database create securehire-db \
  --language=python \
  --source-root=src/backend

codeql analyze securehire-db \
  python-security-and-quality.qls \
  --format=sarif-latest \
  --output=reports/codeql-results.sarif
```

---

## 8. Demo Day Checklist

### Night Before (June 11)

```bash
# 1. Full restart — clean slate
docker compose -f docker/docker-compose.yml down -v
docker compose -f docker/docker-compose.yml up -d

# 2. Verify all containers green
docker ps

# 3. Health check
curl http://localhost:8000/health

# 4. Register test users (save credentials to a text file!)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@test.com","password":"Admin@123","full_name":"Admin","role":"admin"}'

curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"employer@test.com","password":"Secure@123","full_name":"Employer","role":"employer"}'

curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"applicant@test.com","password":"Secure@123","full_name":"Applicant","role":"applicant"}'

# 5. Verify Prometheus scraping
curl http://localhost:9090/api/v1/targets | python3 -m json.tool | grep health

# 6. Open Grafana and confirm dashboards load
#    http://localhost:3000

# 7. Confirm ZAP report exists
ls -la reports/zap-scan-report.html

# 8. Make sure anomaly log is accessible
docker cp securehire-backend:/app/logs/anomalies.log ./reports/
```

### Demo Day Order (June 12)

```
[Minute 0-2]   Show running docker ps → all containers green
[Minute 2-5]   Show frontend at localhost:5173, register + login
[Minute 5-8]   RED TEAM runs brute_force_test.py
[Minute 8-10]  BLUE TEAM shows logs catching it in real-time
[Minute 10-12] RED TEAM tries SQL injection → all blocked
[Minute 12-14] BLUE TEAM shows Prometheus spike in Grafana
[Minute 14-16] Show Docker security: non-root, read-only FS
[Minute 16-18] Show K8s: pod security context, network policies
[Minute 18-20] Show ZAP report + Trivy scan results + SonarQube
[Minute 20-22] Explain QRadar architecture + Falco alerts
[Minute 22-25] Framework mapping: NIST CSF, OWASP, MITRE ATT&CK
```

### Emergency Quick Commands

```bash
# Backend crashed? Restart it
docker compose -f docker/docker-compose.yml restart backend

# See why backend crashed
docker logs securehire-backend --tail 50

# Database connection issue? Reset it
docker compose -f docker/docker-compose.yml restart postgres
sleep 10
docker compose -f docker/docker-compose.yml restart backend

# Everything broken? Full reset (loses data — have test users script ready)
docker compose -f docker/docker-compose.yml down && \
docker compose -f docker/docker-compose.yml up -d

# K8s pod crashed?
kubectl describe pod -l app=securehire-backend
kubectl logs -l app=securehire-backend --previous
kubectl rollout restart deployment/securehire-backend
```

---

*Guide prepared for CYC386 Final Lab — SecureHire | COMSATS University Islamabad | June 12, 2026*
