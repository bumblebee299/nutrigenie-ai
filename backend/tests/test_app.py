# Backend smoke tests — verify the FastAPI application loads and routes respond correctly.

import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app

_TRANSPORT = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_openapi_schema_is_available() -> None:
    """The OpenAPI schema endpoint must respond with HTTP 200 in development."""
    async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
        response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_unknown_route_returns_404() -> None:
    """Requests to unknown routes should return HTTP 404."""
    async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
        response = await client.get("/nonexistent-route")
    assert response.status_code == 404
