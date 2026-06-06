#!/usr/bin/env bash
# ============================================================
# SecureHire — One-Click Setup Script
# CYC386 Final Project
# Usage: bash setup.sh
# ============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()    { echo -e "${GREEN}[✓]${NC} $1"; }
warn()   { echo -e "${YELLOW}[!]${NC} $1"; }
error()  { echo -e "${RED}[✗]${NC} $1"; }
header() { echo -e "\n${BLUE}══════════════════════════════════════${NC}"; echo -e "${BLUE}  $1${NC}"; echo -e "${BLUE}══════════════════════════════════════${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/src/backend"
FRONTEND_DIR="$SCRIPT_DIR/src/frontend"

# ── 1. Check prerequisites ────────────────────────────────────────────────────
header "Checking Prerequisites"

check_cmd() {
    if command -v "$1" &>/dev/null; then
        log "$1 found: $(command -v $1)"
    else
        error "$1 not found — please install it first"
        exit 1
    fi
}

check_cmd python3
check_cmd pip3
check_cmd node
check_cmd npm
check_cmd psql
check_cmd redis-cli
check_cmd docker

PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
log "Python version: $PYTHON_VER"

NODE_VER=$(node --version)
log "Node version: $NODE_VER"

# ── 2. Environment file ────────────────────────────────────────────────────────
header "Setting Up Environment"

if [ ! -f "$BACKEND_DIR/.env" ]; then
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    log ".env file created from .env.example"
    warn "Please review src/backend/.env before running in production"
else
    log ".env already exists"
fi

# ── 3. PostgreSQL setup ────────────────────────────────────────────────────────
header "Setting Up PostgreSQL"

if pg_isready -q 2>/dev/null; then
    log "PostgreSQL is running"
    psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='securehire_db'" | grep -q 1 || {
        psql -U postgres -c "CREATE USER securehire WITH PASSWORD 'securehire123';" 2>/dev/null || true
        psql -U postgres -c "CREATE DATABASE securehire_db OWNER securehire;" 2>/dev/null || true
        log "Database 'securehire_db' created"
    }
    log "Database ready"
else
    warn "PostgreSQL not running locally. If using Docker, this is fine — run docker compose instead."
fi

# ── 4. Backend Python packages ────────────────────────────────────────────────
header "Installing Backend Dependencies"

cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    log "Virtual environment created"
fi

source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
log "Python packages installed"

# ── 5. Frontend packages ───────────────────────────────────────────────────────
header "Installing Frontend Dependencies"

cd "$FRONTEND_DIR"
npm install --silent
log "Node packages installed"

# ── 6. Summary ────────────────────────────────────────────────────────────────
header "Setup Complete!"

echo ""
echo -e "${GREEN}Option A — Run locally (Redis + PostgreSQL must be running):${NC}"
echo ""
echo "  # Terminal 1 — Backend:"
echo "  cd src/backend && source venv/bin/activate"
echo "  uvicorn main:app --reload --port 8000"
echo ""
echo "  # Terminal 2 — Frontend:"
echo "  cd src/frontend && npm run dev"
echo ""
echo -e "${GREEN}Option B — Run with Docker Compose (recommended):${NC}"
echo ""
echo "  cd docker && docker compose up --build"
echo ""
echo -e "${BLUE}Endpoints:${NC}"
echo "  API:       http://localhost:8000"
echo "  API Docs:  http://localhost:8000/api/docs  (DEBUG=True)"
echo "  Frontend:  http://localhost:5173 (local) or http://localhost:3000 (Docker)"
echo "  Metrics:   http://localhost:8000/metrics"
echo "  Grafana:   http://localhost:3001  (admin / admin123)"
echo ""
