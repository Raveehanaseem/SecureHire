"""
OPA (Open Policy Agent) Integration
- Attribute-Based Access Control (ABAC) via OPA REST API
- Falls back to built-in RBAC if OPA is unavailable
CYC386 Requirement: OPA policies + ABAC
"""

import httpx
import logging
from fastapi import HTTPException, status
from typing import Optional

logger = logging.getLogger(__name__)

OPA_URL = "http://localhost:8181"


async def evaluate_policy(
    policy_path: str,
    input_data: dict,
) -> bool:
    """
    Query OPA for a policy decision.
    policy_path: e.g. "securehire/authz/allow"
    input_data: the full input document sent to OPA
    """
    url = f"{OPA_URL}/v1/data/{policy_path.replace('.', '/')}"
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.post(url, json={"input": input_data})
            resp.raise_for_status()
            result = resp.json()
            decision = result.get("result", False)
            logger.debug(f"OPA decision [{policy_path}]: {decision} | input: {input_data}")
            return bool(decision)
    except Exception as e:
        logger.warning(f"OPA unavailable ({e}), falling back to built-in RBAC")
        return None  # Caller should fall back


async def abac_check(
    user_id: str,
    role: str,
    resource: str,
    action: str,
    resource_owner_id: Optional[str] = None,
) -> bool:
    """
    ABAC check via OPA. Falls back to RBAC if OPA is down.
    """
    input_doc = {
        "user": {
            "id": user_id,
            "role": role,
        },
        "action": action,
        "resource": resource,
        "resource_owner_id": resource_owner_id,
    }

    result = await evaluate_policy("securehire/authz/allow", input_doc)

    if result is None:
        # OPA unavailable — use built-in RBAC fallback
        from auth.dependencies import ROLE_PERMISSIONS, Role
        try:
            role_enum = Role(role)
            perms = ROLE_PERMISSIONS.get(role_enum, {})
            return action in perms.get(resource, [])
        except ValueError:
            return False

    return result


def require_abac(resource: str, action: str):
    """FastAPI dependency for ABAC checks via OPA."""
    from fastapi import Depends
    from auth.dependencies import get_current_user

    async def checker(current_user=Depends(get_current_user)):
        allowed = await abac_check(
            user_id=str(current_user.id),
            role=current_user.role,
            resource=resource,
            action=action,
        )
        if not allowed:
            logger.warning(
                f"ABAC denied | User: {current_user.id} | Role: {current_user.role} "
                f"| Resource: {resource} | Action: {action}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied by policy",
            )
        return current_user

    return checker
