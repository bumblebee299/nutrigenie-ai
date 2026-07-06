"""IBM Cloud Object Storage client — lazy initialisation so missing credentials don't crash startup."""

import structlog
from typing import Optional

logger = structlog.get_logger(__name__)

_client: Optional[object] = None


def get_cos_client():  # type: ignore[return]
    """
    Return an authenticated IBM COS client.

    Raises:
        RuntimeError: if COS_API_KEY or COS_INSTANCE_CRN are not configured.
    """
    global _client
    if _client is not None:
        return _client

    from backend.api.config import settings

    if not settings.COS_API_KEY or not settings.COS_INSTANCE_CRN:
        raise RuntimeError(
            "IBM Cloud Object Storage is not configured. "
            "Set COS_API_KEY and COS_INSTANCE_CRN in your .env file."
        )

    import ibm_boto3
    from ibm_botocore.client import Config

    _client = ibm_boto3.client(
        "s3",
        ibm_api_key_id=settings.COS_API_KEY,
        ibm_service_instance_id=settings.COS_INSTANCE_CRN,
        config=Config(signature_version="oauth"),
        endpoint_url=settings.COS_ENDPOINT,
    )
    logger.info("IBM COS client initialised", endpoint=settings.COS_ENDPOINT)
    return _client


class _LazyCoS:
    """Proxy that defers the real client creation until first use."""

    def __getattr__(self, name: str):  # type: ignore[override]
        return getattr(get_cos_client(), name)


cos_client = _LazyCoS()
