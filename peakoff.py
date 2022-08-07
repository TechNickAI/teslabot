from Tessie import Tessie
import arrow
import click
from loguru import logger
from utils import send_sms


@click.command()
@click.option("--vin", required=True, help="Tesla VIN number to auto vent")
@click.option("--tessie_token", required=True, help="API access token for Tessie (see tessie.com)")
@click.option("--peak-start", required=True, help="When peak pricing starts, in military time. Ex: 16:00")
@click.option("--peak-end", required=True, help="When peak pricing ends, in military time. Ex: 21:00")
@click.option("--notify_phone", help="Send a message to this phone number when the windows are moved")
def peakoff(vin, tessie_token, peak_start, peak_end, notify_phone):
    """
    Automatically stop charging during peak electricity hours
    """
    tessie = Tessie(tessie_token, vin)
    state = tessie.get_vehicle_state()
    charge_state = state["charge_state"]
    logger.debug(f"Charge state: {charge_state}")

    if not charge_state["charge_port_door_open"]:
        logger.warning("Car is not plugged in, exiting")
        return

    if charge_state["charger_voltage"] > 240:
        logger.warning(f"Charging voltage is {charge_state['charger_voltage']}, likely at a supercharger, exiting")
        return

    msg = f"Battery level is {charge_state['battery_level']}% and is {charge_state['charging_state']}."
    logger.info(msg)

    local_time = arrow.utcnow().shift(seconds=state["vehicle_config"]["utc_offset"]).format("HH:mm")
    logger.info(f"Local time is {local_time}")

    if charge_state["charging_state"] == "Charging":
        if local_time > peak_start and local_time < peak_end:
            logger.info("Charging during peak time")
            tessie.request("command/stop_charging", vin)
            logger.success("Charging stopped")
            if notify_phone:
                msg += " Charging stopped during peak ours. ✅"
                send_sms(notify_phone, msg)
        else:
            logger.info("Leaving charging as is")
    elif charge_state["charging_state"] == "Stopped":
        if local_time > peak_end:
            logger.info("Off peak time, resuming charging")
            tessie.request("command/start_charging", vin)
            logger.success("Charging started")
            if notify_phone:
                msg += " Charging restarted after peak hours ✅"
                send_sms(notify_phone, msg)
        else:
            logger.info("Leaving charging stopped during peak")


if __name__ == "__main__":
    peakoff()
