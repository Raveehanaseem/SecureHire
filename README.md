# SecureHire -- Person A Deliverables

CYC386 Secure Software Design and Development

## Contents

### /docs/
- SRD_SecureHire_v1.0.docx              -- Security Requirements Document (Phase 1)
- ASVS_v5.0_Checklist_SecureHire.xlsx   -- OWASP ASVS v5.0 controls checklist (Phase 1 & 7)
- NIST_CSF_MultiFramework_Mapping.xlsx  -- NIST CSF + ASVS + ISO 27034 + CSA CCM mapping (Phase 1 & 7)
- Executive_Security_Report.docx        -- Final executive report 8-10 pages (Phase 7)

### /reports/
- CIS_Docker_Benchmark_Report.docx      -- CIS Docker Benchmark v1.6.0 assessment (Phase 4)

### /src/auth_service/
- schemas.py    -- Pydantic v2 input validation for Auth Service (Phase 3)

### /src/task_service/
- schemas.py    -- Pydantic v2 input validation for Task Service (Phase 3)

## How to use the Pydantic schemas

Copy src/auth_service/schemas.py into your auth_service directory.
Copy src/task_service/schemas.py into your task_service directory.

In your FastAPI route handlers, import and use the models as request bodies:

    from schemas import RegisterRequest, LoginRequest

    @router.post("/register")
    def register(body: RegisterRequest, db: Session = Depends(get_db)):
        ...

FastAPI will automatically validate incoming requests against the model
and return HTTP 422 Unprocessable Entity with detailed field errors if validation fails.

## How to run the CIS Docker Benchmark

With your SecureHire containers running:

    git clone https://github.com/docker/docker-bench-security.git
    cd docker-bench-security
    sudo bash docker-bench-security.sh -l /tmp/docker_bench_results.log

Review /tmp/docker_bench_results.log and compare against the report in /reports/.
