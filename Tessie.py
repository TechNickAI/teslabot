import requests
from loguru import logger


class Tessie:

    tessie_token = None

    def __init__(self, tessie_token):
        self.tessie_token = tessie_token

    def get_vehicles(self):
        return self.request("vehicles")

    def get_vehicle_state(self, vin):
        vehicle_states = self.get_vehicles()
        for result in vehicle_states["results"]:
            if vin == result["vin"]:
                return result["last_state"]
        else:
            raise Exception(f"No matching VIN found #{vin}")

    def request(self, path, vin=None):
        base_url = "https://api.tessie.com/"

        if vin:
            base_url = f"{base_url}/{vin}"

        url = f"{base_url}/{path}"
        logger.info(f"Requesting {url}")

        response = requests.get(url, headers={"Authorization": f"Bearer {self.tessie_token}"})
        response.raise_for_status()
        return response.json()
