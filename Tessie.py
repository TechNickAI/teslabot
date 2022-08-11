import arrow
import requests
from loguru import logger


class Tessie:
    """

    Class for interacting with the Tessie API

    """

    # Internal state
    tessie_token = state = vin = None

    def __init__(self, tessie_token, vin=None):
        self.tessie_token = tessie_token
        self.vin = vin

    def get_vehicles(self):
        return self.request("vehicles")

    def get_vehicle_state(self):
        if self.state:
            return self.state

        state = self.request("state", self.vin)
        state_date = arrow.get(state["drive_state"]["timestamp"])
        logger.success(f"Retrieved state for {state['display_name']} as of {state_date.humanize()}")

        self.state = state
        return state

    def check_state(self, key, sub_key, func, message):
        state = self.get_vehicle_state()
        data = state[key].get(sub_key)

        if func(data):
            return True
        else:
            logger.debug(f"{key}:{sub_key} did not pass test with value '{data}'")
            raise ValueError(message)

    def get_sleep_status(self):
        return self.request("status", self.vin)["status"]

    def wake_up(self):
        sleep_status = self.get_sleep_status()
        logger.info(f"Sleep status is {sleep_status}")
        if sleep_status != "awake":
            logger.info("Sending wake up")
            self.request("wake", self.vin)
            logger.success("Awake")

    def request(self, path, vin=None):
        base_url = "https://api.tessie.com"

        if vin:
            base_url = f"{base_url}/{vin}"

        url = f"{base_url}/{path}"
        logger.trace(f"Requesting {url}")

        response = requests.get(url, headers={"Authorization": f"Bearer {self.tessie_token}"})
        response.raise_for_status()
        return response.json()

    def localize_time(self, time: arrow):
        return time.shift(seconds=self.state["vehicle_config"]["utc_offset"])
