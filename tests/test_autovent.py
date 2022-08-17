import json

import arrow

from autovent import autovent
from utils import f2c


def test_autovent(requests_mock):

    mock_data = json.loads(open("tests/mock_data/parked.json").read())
    mock_data["drive_state"]["timestamp"] = arrow.utcnow().timestamp() * 1000
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    assert autovent("dummy_vin", "dummy_tessie_token", 90, None) == 0, "Initial load should do nothing"

    mock_data["climate_state"]["inside_temp"] = f2c(95)
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    requests_mock.get("https://api.tessie.com/dummy_vin/status", text='{"status": "awake"}')
    requests_mock.get("https://api.tessie.com/dummy_vin/command/vent_windows", text='{"result": true }')
    assert autovent("dummy_vin", "dummy_tessie_token", 90, None) == -1, "Windows should roll down"
    mock_data["vehicle_state"]["rd_window"] = 1

    mock_data["climate_state"]["inside_temp"] = f2c(85)
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    requests_mock.get("https://api.tessie.com/dummy_vin/command/close_windows", text='{"result": true }')
    assert autovent("dummy_vin", "dummy_tessie_token", 90, None) == 1, "Windows should roll back up"
