"""Cloudant database client — lazy initialisation so missing credentials don't crash startup."""

import structlog
from typing import Optional

logger = structlog.get_logger(__name__)

_client: Optional[object] = None


def get_cloudant_client():  # type: ignore[return]
    """
    Return an authenticated Cloudant client.

    Raises:
        RuntimeError: if CLOUDANT_URL or CLOUDANT_API_KEY are not configured.
    """
    global _client
    if _client is not None:
        return _client

    from backend.api.config import settings

    if not settings.CLOUDANT_URL or not settings.CLOUDANT_API_KEY:
        raise RuntimeError(
            "IBM Cloudant is not configured. "
            "Set CLOUDANT_URL and CLOUDANT_API_KEY in your .env file."
        )

    from ibmcloudant.cloudant_v1 import CloudantV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

    authenticator = IAMAuthenticator(settings.CLOUDANT_API_KEY)
    client = CloudantV1(authenticator=authenticator)
    client.set_service_url(settings.CLOUDANT_URL)
    _client = client
    logger.info("Cloudant client initialised", url=settings.CLOUDANT_URL)
    return _client


# Module-level proxy — services call cloudant_client.method(...)
class _LazyCloudant:
    """Proxy that defers the real client creation until first use."""

    def __getattr__(self, name: str):  # type: ignore[override]
        return getattr(get_cloudant_client(), name)


cloudant_client = _LazyCloudant()
