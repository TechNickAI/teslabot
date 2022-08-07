import json

from autovent import autovent
from utils import f2c


def test_autovent(requests_mock):
    mock_data = json.loads(open("tests/mock_data/parked.json").read())
    requests_mock.get("https://api.tessie.com/vehicles", text=json.dumps(mock_data))
    assert autovent("5YJ3E1EA8KF326283", "dummy_tessie_token", 90, None) == 0, "Initial load should do nothing"

    mock_data["results"][0]["last_state"]["climate_state"]["inside_temp"] = f2c(95)
    requests_mock.get("https://api.tessie.com/vehicles", text=json.dumps(mock_data))
    requests_mock.get("https://api.tessie.com/5YJ3E1EA8KF326283/status", text='{"status": "awake"}')
    requests_mock.get("https://api.tessie.com/5YJ3E1EA8KF326283/command/vent_windows", text='{"result": true }')
    assert autovent("5YJ3E1EA8KF326283", "dummy_tessie_token", 90, None) == -1, "Windows should roll down"
    mock_data["results"][0]["last_state"]["vehicle_state"]["rd_window"] = 1

    mock_data["results"][0]["last_state"]["climate_state"]["inside_temp"] = f2c(85)
    requests_mock.get("https://api.tessie.com/vehicles", text=json.dumps(mock_data))
    requests_mock.get("https://api.tessie.com/5YJ3E1EA8KF326283/command/close_windows", text='{"result": true }')
    assert autovent("5YJ3E1EA8KF326283", "dummy_tessie_token", 90, None) == 1, "Windows should roll back up"
