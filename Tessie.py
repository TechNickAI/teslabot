from loguru import logger
from timezonefinder import TimezoneFinder
import arrow, requests


class Tessie:
    """

    Class for interacting with the Tessie API

    """

    # Internal state
    tessie_token = state = vin = session = None

    def __init__(self, tessie_token, vin=None):
        self.tessie_token = tessie_token
        self.vin = vin

    def get_vehicle_state(self):
        if self.state:
            return self.state

        state = self.request("state", self.vin)
        state_date = arrow.get(state["drive_state"]["timestamp"])
        logger.info(f"Retrieved state for {state['display_name']} (#{state['vin']}) as of {state_date.humanize()}")

        self.state = state
        return state

    def check_state(self, key, sub_key, func, message):
        # Convenience method to check the value of a state against an expected value
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
        logger.debug(f"Sleep status is {sleep_status}")
        if sleep_status != "awake":
            logger.info("Sending wake up")
            self.request("wake", self.vin)
            logger.success("Awake")

    def get_car_time(self):
        # For the supplied time, shift from UTC via the lat/long
        timezone = TimezoneFinder().timezone_at(
            lng=self.state["drive_state"]["longitude"], lat=self.state["drive_state"]["latitude"]
        )
        return arrow.utcnow().to(timezone)

    def are_windows_open(self):
        vehicle_state = self.get_vehicle_state()["vehicle_state"]
        return any(
            [
                vehicle_state["fd_window"],
                vehicle_state["rd_window"],
                vehicle_state["fp_window"],
                vehicle_state["rp_window"],
            ]
        )

    def request(self, path, vin=None):
        # Set up a requests session, which enables keep alive and allows for retries
        if self.session is None:
            self.session = requests.Session()

        base_url = "https://api.tessie.com"

        if vin:
            base_url = f"{base_url}/{vin}"

        url = f"{base_url}/{path}"
        logger.trace(f"Requesting {url}")

        response = self.session.get(url, headers={"Authorization": f"Bearer {self.tessie_token}"}, timeout=30)
        response.raise_for_status()
        return response.json()
