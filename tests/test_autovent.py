from autovent import autovent
from utils import f2c
import arrow, json


def test_stale_data(requests_mock):

    mock_data = json.loads(open("tests/mock_data/parked.json").read())

    requests_mock.post("https://api.twilio.com/2010-04-01/Accounts/ACXXX/Messages.json", text='{"sid": "SMXXX"}')

    # Stale data
    mock_data["drive_state"]["timestamp"] = arrow.utcnow().shift(hours=-12).timestamp() * 1000
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    assert (
        autovent("dummy_vin", "dummy_tessie_token", 90, "+18005551212") is None
    ), "Should leave the car sleeping at night"

    mock_data["drive_state"]["timestamp"] = arrow.utcnow().shift(hours=-5).timestamp() * 1000
    requests_mock.get("https://api.tessie.com/dummy_vin/status", text='{"status": "asleep"}')
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    requests_mock.get("https://api.tessie.com/dummy_vin/wake", text='{"result": true }')
    assert (
        autovent("dummy_vin", "dummy_tessie_token", 90, "+18005551212") is None
    ), "Should wake up the car during the day"


def test_autovent(requests_mock):

    mock_data = json.loads(open("tests/mock_data/parked.json").read())
    mock_data["drive_state"]["timestamp"] = arrow.utcnow().timestamp() * 1000

    requests_mock.post("https://api.twilio.com/2010-04-01/Accounts/ACXXX/Messages.json", text='{"sid": "SMXXX"}')
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    assert autovent("dummy_vin", "dummy_tessie_token", 90, "+18005551212") == 0, "Initial load should do nothing"

    # Conditions
    mock_data["drive_state"]["speed"] = 10
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    assert (
        autovent("dummy_vin", "dummy_tessie_token", 90, "+18005551212") is None
    ), "Should not vent if the car is moving"
    mock_data["drive_state"]["speed"] = None

    # Let's make it hot
    mock_data["climate_state"]["inside_temp"] = f2c(95)
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    requests_mock.get("https://api.tessie.com/dummy_vin/status", text='{"status": "awake"}')
    requests_mock.get("https://api.tessie.com/dummy_vin/command/vent_windows", text='{"result": true }')
    assert autovent("dummy_vin", "dummy_tessie_token", 90, "+18005551212") == -1, "Windows should roll down"
    mock_data["vehicle_state"]["rd_window"] = 1

    # Let's cool it down
    mock_data["climate_state"]["inside_temp"] = f2c(85)
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    requests_mock.get("https://api.tessie.com/dummy_vin/command/close_windows", text='{"result": true }')
    assert autovent("dummy_vin", "dummy_tessie_token", 90, "+18005551212") == 1, "Windows should roll back up"
