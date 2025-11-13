from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_battery_soc_route():
    response = client.get("/kostal/batterysoc")
    assert response.status_code == 200
    data = response.json()
    assert "entity_id" in data
    assert "battery_soc" in data
    assert "unit_of_measurement" in data

def test_battery_power_in_route():
    response = client.get("/kostal/batterypowerin")
    assert response.status_code == 200
    data = response.json()
    assert "entity_id" in data
    assert "battery_power_in" in data
    assert "unit_of_measurement" in data

def test_battery_power_out_route():
    response = client.get("/kostal/batterypowerout")
    assert response.status_code == 200
    data = response.json()
    assert "entity_id" in data
    assert "battery_power_out" in data
    assert "unit_of_measurement" in data


def test_total_dc_input_route():
    response = client.get("/kostal/totaldcinput")
    assert response.status_code == 200
    data = response.json()
    assert "entity_id" in data
    assert "TOTAL_DC_INPUT" in data
    assert "unit_of_measurement" in data


def test_home_power_route():
    response = client.get("/kostal/homepower")
    assert response.status_code == 200
    data = response.json()
    assert "entity_id" in data
    assert "HOME_POWER" in data
    assert "unit_of_measurement" in data

def test_total_home_consumption_route():
    response = client.get("/kostal/totalhomeconsumption")
    assert response.status_code == 200
    data = response.json()
    assert "entity_id" in data
    assert "TOTAL_HOME_CONSUMPTION" in data
    assert "unit_of_measurement" in data

def test_total_energy_to_grid_route():
    response = client.get("/kostal/totalenergytogrid")
    assert response.status_code == 200
    data = response.json()
    assert "entity_id" in data
    assert "TOTAL_ENERGY_TO_GRID" in data
    assert "unit_of_measurement" in data

def test_total_ernergy_from_grid_route():
    response = client.get("/kostal/totalenergyfromgrid")
    assert response.status_code == 200
    data = response.json()
    assert "entity_id" in data
    assert "TOTAL_ENERGY_FROM_GRID" in data
    assert "unit_of_measurement" in data
