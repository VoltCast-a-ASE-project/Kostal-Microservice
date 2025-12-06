import pytest
from unittest.mock import AsyncMock, patch
from app.kostal_service import KostalService


@pytest.fixture
def ha_mock():
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_realtime_data_returns_expected_json(ha_mock):
    ha_mock.get_entity_state.side_effect = ["100", "250", "80"]
    service = KostalService(ha_mock)

    with patch("app.kostal_service.build_live_json", return_value={"ok": True}) as json_mock:
        result = await service.get_realtime_data()

        assert result == {"ok": True}
        json_mock.assert_called_once_with("100", "250", "80")
        assert ha_mock.get_entity_state.call_count == 3


@pytest.mark.asyncio
async def test_get_lf_data_returns_interval_json(ha_mock):
    ha_mock.get_entity_state.side_effect = ["5000", "4300"]
    service = KostalService(ha_mock)

    with patch("app.kostal_service.build_interval_json", return_value={"interval": True}) as json_mock:
        result = await service.get_lf_data()

        assert result == {"interval": True}
        json_mock.assert_called_once_with("5000", "4300")


@pytest.mark.asyncio
async def test_get_historical_data_uses_db_functions():
    with patch("app.kostal_service.get_today_consumption", return_value=5), \
         patch("app.kostal_service.get_last_30_days", return_value=[1, 2, 3]), \
         patch("app.kostal_service.get_last_365_days", return_value=[10, 20, 30]), \
         patch("app.kostal_service.build_history_json", return_value={"history": True}) as json_mock:

        result = await KostalService.get_historical_data()

        assert result == {"history": True}
        json_mock.assert_called_once_with(5, [1, 2, 3], [10, 20, 30])
