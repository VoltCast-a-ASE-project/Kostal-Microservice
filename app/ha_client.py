import os
from dotenv import load_dotenv
from app.inverter_db import get_ipadress, get_token
import httpx

load_dotenv()

class HAClient:
    def __init__(self):
        self.base_url = get_ipadress()
        self.token = get_token()



        if not self.base_url:
            raise ValueError("HA_REST_URL is missing!")
        if not self.token:
            raise ValueError("HA_TOKEN is missing!")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def get_entity_state(self, entity_id: str) -> dict:
        url = f"{self.base_url}/api/states/{entity_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
