import os
import pytest
import respx
from httpx import Response
from app.ha_client import HAClient

@pytest.mark.asyncio
@respx.mock
async def test_get_entity_state(monkeypatch):
    monkeypatch.setenv("HA_REST_URL", "http://test-ha")
    monkeypatch.setenv("HA_TOKEN", "dummy")

    respx.get("http://test-ha/api/states/sensor.test").mock(
        return_value=Response(200, json={"state": "1", "attributes": {}})
    )

    client = HAClient()
    data = await client.get_entity_state("sensor.test")

    assert data["state"] == "1"

def test_ha_client_missing_base_url(monkeypatch):
    monkeypatch.delenv("HA_REST_URL", raising=False)
    monkeypatch.setenv("HA_TOKEN", "dummy")

    with pytest.raises(ValueError, match="HA_REST_URL is missing!"):
        HAClient()


def test_ha_client_missing_token(monkeypatch):
    monkeypatch.setenv("HA_REST_URL", "http://test-ha")
    monkeypatch.delenv("HA_TOKEN", raising=False)

    with pytest.raises(ValueError, match="HA_TOKEN is missing!"):
        HAClient()