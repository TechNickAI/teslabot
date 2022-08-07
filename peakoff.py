import arrow
import click
from loguru import logger

from Tessie import Tessie
from utils import send_sms


def peakoff(vin, tessie_token, peak_start, peak_end, notify_phone):
    """

    Automatically stop charging during peak electricity hours

    """
    tessie = Tessie(tessie_token, vin)
    state = tessie.get_vehicle_state()
    charge_state = state["charge_state"]
    logger.trace(f"Charge state: {charge_state}")

    try:
        if tessie.localize_time(arrow.utcnow().shift(hours=-2)) > tessie.localize_time(
            arrow.get(state["drive_state"]["timestamp"])
        ):
            raise ValueError("API data is stale. Car not online?")

        tessie.check_state("drive_state", "speed", lambda v: v is None, "Car is moving 🛞")
        tessie.check_state(
            "charge_state", "charging_state", lambda v: v in ["Charging", "Stopped"], "Cable not plugged in"
        )
        tessie.check_state("charge_state", "charge_port_door_open", lambda v: v, "Charge port is closed")
        tessie.check_state("charge_state", "charger_voltage", lambda v: v < 240, "Charging at a super charger 🔋")
        tessie.check_state("vehicle_state", "is_user_present", lambda v: not v, "Someone is in the car 🙆")
    except ValueError as e:
        logger.critical(str(e))
        return None

    msg = f"🔋Battery level is {charge_state['battery_level']}% and is {charge_state['charging_state']}."
    logger.info(msg)

    local_time = tessie.localize_time(arrow.utcnow()).format("HH:mm")
    logger.info(f"Local time is {local_time}")

    if charge_state["charging_state"] == "Charging":
        if local_time > peak_start and local_time < peak_end:
            logger.warning("Charging during peak time")
            tessie.request("command/stop_charging", vin)
            logger.success("Charging stopped 🛑")
            if notify_phone:
                msg += " Charging stopped during peak ours. ✅"
                send_sms(notify_phone, msg)
            return -1
        else:
            logger.info("Leaving charging as is")
            return 0

    elif charge_state["charging_state"] == "Stopped":
        if local_time > peak_end:
            logger.info("Off peak time, resuming charging")
            tessie.request("command/start_charging", vin)
            logger.success("Charging started 🔌")
            if notify_phone:
                msg += "🔋Charging restarted after peak hours ✅"
                send_sms(notify_phone, msg)
            return 1

        else:
            logger.info("Leaving charging stopped during peak")
            return 0


if __name__ == "__main__":

    @click.command()
    @click.option("--vin", required=True, help="Tesla VIN number to auto vent")
    @click.option("--tessie_token", required=True, help="API access token for Tessie (see tessie.com)")
    @click.option("--peak-start", required=True, help="When peak pricing starts, in military time. Ex: 16:00")
    @click.option("--peak-end", required=True, help="When peak pricing ends, in military time. Ex: 21:00")
    @click.option("--notify_phone", help="Send a message to this phone number when the windows are moved")
    def peakoff_command(vin, tessie_token, peak_start, peak_end, notify_phone):
        peakoff(vin, tessie_token, peak_start, peak_end, notify_phone)

    peakoff()
