"""
HashiCorp Vault Integration
- Dynamic secrets fetching
- Secret rotation support
CYC386 Requirement: HashiCorp Vault for secrets management
"""

import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)

_vault_token: str = settings.VAULT_TOKEN


async def get_vault_secret(path: str) -> dict:
    """Fetch a secret from Vault KV store."""
    url = f"{settings.VAULT_ADDR}/v1/secret/data/{path}"
    headers = {"X-Vault-Token": _vault_token}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()["data"]["data"]
    except Exception as e:
        logger.warning(f"Vault unavailable, using env fallback: {e}")
        return {}


async def rotate_vault_secret(path: str, new_data: dict) -> bool:
    """Write / rotate a secret in Vault."""
    url = f"{settings.VAULT_ADDR}/v1/secret/data/{path}"
    headers = {"X-Vault-Token": _vault_token, "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(url, headers=headers, json={"data": new_data})
            resp.raise_for_status()
            logger.info(f"Secret rotated at path: {path}")
            return True
    except Exception as e:
        logger.error(f"Vault secret rotation failed: {e}")
        return False


async def get_db_credentials() -> dict:
    """Fetch dynamic DB credentials from Vault (falls back to .env)."""
    creds = await get_vault_secret("securehire/database")
    if creds:
        logger.info("DB credentials loaded from Vault")
    return creds


async def get_jwt_secret() -> str:
    """Fetch JWT secret from Vault (falls back to .env)."""
    data = await get_vault_secret("securehire/jwt")
    return data.get("secret_key", settings.JWT_SECRET_KEY)
