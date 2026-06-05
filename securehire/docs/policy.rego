package securehire.authz

# Default deny
default allow = false

# Admin can do everything
allow {
    input.user.role == "admin"
}

# Employer can read/write/delete their own jobs
allow {
    input.user.role == "employer"
    input.resource == "jobs"
    input.action == "read"
}

allow {
    input.user.role == "employer"
    input.resource == "jobs"
    input.action == "write"
}

allow {
    input.user.role == "employer"
    input.resource == "jobs"
    input.action == "delete"
    input.user.id == input.resource_owner_id
}

# Employer can read applications on their jobs
allow {
    input.user.role == "employer"
    input.resource == "applications"
    input.action == "read"
}

# Applicant can read jobs and manage their own applications
allow {
    input.user.role == "applicant"
    input.resource == "jobs"
    input.action == "read"
}

allow {
    input.user.role == "applicant"
    input.resource == "applications"
    input.action == "write"
}

allow {
    input.user.role == "applicant"
    input.resource == "applications"
    input.action == "read"
    input.user.id == input.resource_owner_id
}

allow {
    input.user.role == "applicant"
    input.resource == "profile"
    input.action == "read"
}

allow {
    input.user.role == "applicant"
    input.resource == "profile"
    input.action == "write"
}
