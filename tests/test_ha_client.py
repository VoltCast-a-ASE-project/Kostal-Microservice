import pytest
import respx
from httpx import Response

from app.ha_client import HAClient


@pytest.mark.asyncio
@respx.mock
async def test_get_entity_state(monkeypatch):
    # HAClient zieht base_url/token aus DB-gettern -> die mocken wir
    monkeypatch.setattr("app.ha_client.get_ipadress", lambda: "http://test-ha")
    monkeypatch.setattr("app.ha_client.get_token", lambda: "dummy")

    respx.get("http://test-ha/api/states/sensor.test").mock(
        return_value=Response(200, json={"state": "1", "attributes": {}})
    )

    client = HAClient()
    data = await client.get_entity_state("sensor.test")

    assert data["state"] == "1"


def test_ha_client_missing_base_url(monkeypatch):

    monkeypatch.setattr("app.ha_client.get_ipadress", lambda: "")
    monkeypatch.setattr("app.ha_client.get_token", lambda: "dummy")

    with pytest.raises(ValueError, match="HA_REST_URL is missing!"):
        HAClient()


def test_ha_client_missing_token(monkeypatch):
    # token fehlt -> ValueError erwartet
    monkeypatch.setattr("app.ha_client.get_ipadress", lambda: "http://test-ha")
    monkeypatch.setattr("app.ha_client.get_token", lambda: "")

    with pytest.raises(ValueError, match="HA_TOKEN is missing!"):
        HAClient()
