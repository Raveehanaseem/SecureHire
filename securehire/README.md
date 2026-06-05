# SecureHire 🔐
**Secure Job Recruitment Platform — CYC386 Final Project**
COMSATS University Islamabad | Spring 2026

---

## Team Roles
| Person | Role | Branch |
|--------|------|--------|
| Person A | SRD, Threat Model, Architecture Docs | `person-a/docs-security-design` |
| Person B | Backend API + Frontend App | `person-b/app-developer` |
| Person C | Docker, Kubernetes, Terraform | `person-c/docker-infra` |
| Person D | ZAP Pentesting, Red Team Demo | `person-d/security-testing` |

---

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.11) |
| Frontend | React + Vite + TailwindCSS |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Events | Apache Kafka |
| Auth | JWT + OAuth2.0 + RBAC/ABAC |
| Encryption | AES-256-GCM |
| Secrets | HashiCorp Vault |
| Policies | OPA (Open Policy Agent) |
| AI/ML | Anomaly Detection (scikit-learn) |
| Containers | Docker (multi-stage, non-root) |
| Orchestration | Kubernetes + Kyverno |
| IaC | Terraform |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus + Grafana + Falco |

---

## Quick Start

### Option A — Local Development
```bash
bash setup.sh

# Terminal 1 — Backend
cd src/backend && source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd src/frontend && npm run dev
```

### Option B — Docker Compose (Recommended)
```bash
cd docker
docker compose up --build
```

---

## Security Features Implemented
- JWT + OAuth2.0 Authentication
- RBAC + ABAC (OPA policies)
- AES-256-GCM encryption at rest
- HashiCorp Vault integration
- SQLi / XSS / CSRF / SSRF prevention
- Rate limiting + account lockout
- Refresh token rotation + blacklisting
- Security headers (CSP, HSTS, X-Frame-Options)
- AI/ML anomaly detection
- Prometheus metrics
- Docker hardening (multi-stage, non-root, read-only fs)
- Kubernetes Pod Security Standards
- Kyverno policy enforcement
- Falco runtime security rules
- GitHub Actions CI/CD with Trivy + CodeQL + ZAP

---

## API Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | Public | Register |
| POST | `/api/v1/auth/login` | Public | Login |
| POST | `/api/v1/auth/logout` | JWT | Logout |
| POST | `/api/v1/auth/refresh` | Public | Refresh token |
| GET | `/api/v1/auth/me` | JWT | Current user |
| GET | `/api/v1/jobs/` | Public | List jobs |
| POST | `/api/v1/jobs/` | Employer | Create job |
| PATCH | `/api/v1/jobs/{id}/approve` | Admin | Approve job |
| DELETE | `/api/v1/jobs/{id}` | Employer/Admin | Delete job |
| POST | `/api/v1/applications/` | Applicant | Apply |
| GET | `/api/v1/applications/my` | Applicant | My applications |
| GET | `/api/v1/applications/job/{id}` | Employer | Job applicants |
| PATCH | `/api/v1/applications/{id}/status` | Employer | Update status |
| GET | `/metrics` | Internal | Prometheus |
| GET | `/health` | Public | Health check |

---

## Folder Structure
```
securehire/
├── setup.sh                    # One-click setup
├── src/
│   ├── backend/
│   │   ├── main.py             # FastAPI app (updated)
│   │   ├── config.py           # Settings
│   │   ├── database.py         # PostgreSQL
│   │   ├── auth/               # JWT, RBAC, dependencies
│   │   ├── models/             # SQLAlchemy models
│   │   ├── api/v1/             # Route handlers
│   │   ├── middleware/         # Security, rate limiting
│   │   ├── cache/              # Redis client
│   │   ├── kafka/              # Kafka producer
│   │   └── utils/
│   │       ├── encryption.py   # AES-256-GCM
│   │       ├── vault_client.py # HashiCorp Vault (NEW)
│   │       ├── opa_client.py   # OPA ABAC policies (NEW)
│   │       ├── anomaly_detection.py  # AI/ML (NEW)
│   │       ├── metrics.py      # Prometheus (NEW)
│   │       └── logger.py
│   └── frontend/               # React + Vite
├── docker/
│   ├── Dockerfile.backend      # Multi-stage, non-root
│   ├── Dockerfile.frontend     # Nginx hardened
│   └── docker-compose.yml      # Full stack
├── k8s/
│   └── securehire.yaml         # Deployments + NetworkPolicies + Kyverno
├── iac/
│   └── main.tf                 # Terraform + Vault
├── ci/
│   └── github-actions.yml      # CodeQL + Trivy + ZAP + Tests
├── monitor/
│   ├── prometheus/prometheus.yml
│   └── falco/securehire_rules.yaml
├── docs/
│   └── policy.rego             # OPA Rego policy
└── reports/                    # ZAP + Trivy reports go here
```
