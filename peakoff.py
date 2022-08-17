import arrow
import click
from loguru import logger

from Tessie import Tessie
from utils import send_sms

DEFAULT_LOW_BATTERY_THRESHOLD = 42


def peakoff(vin, tessie_token, peak_start, peak_end, notify_phone, low_battery_treshold=DEFAULT_LOW_BATTERY_THRESHOLD):
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

        tessie.check_state("drive_state", "speed", lambda v: v is None, "Car is driving 🛞")
        tessie.check_state("charge_state", "charge_port_door_open", lambda v: v, "Charge cable is not plugged in")
        tessie.check_state("charge_state", "charging_state", lambda v: v != "Complete", "Charging is complete")
        tessie.check_state("charge_state", "charger_voltage", lambda v: v < 240, "Charging at a super charger 🔋")
    except ValueError as e:
        logger.critical(str(e))
        return None

    msg = f"🔋Battery level is {charge_state['battery_level']}% and is {charge_state['charging_state']}"
    logger.info(msg)

    local_time = tessie.localize_time(arrow.utcnow()).format("HH:mm")
    logger.info(f"Local time is {local_time}")

    if charge_state["charging_state"] == "Charging":
        if charge_state["battery_level"] < low_battery_treshold:
            logger.warning(f"Charge level is below {low_battery_treshold}%, allowing charging to continue")
            return 0
        elif local_time > peak_start and local_time < peak_end:
            logger.warning("Charging during peak time! ")
            tessie.request("command/stop_charging", vin)
            if notify_phone:
                msg += f", charging paused during peak hours, will resume at {peak_end} ♻️"
                send_sms(notify_phone, msg)
            return -1
        else:
            logger.info("Leaving charging as is")
            return 0

    elif charge_state["charging_state"] == "Stopped":
        if local_time > peak_end:
            logger.info("Off peak time, resuming charging")
            response = tessie.request("command/start_charging", vin)
            if response["result"]:
                logger.success("Successfully restarted charging")
                if notify_phone:
                    msg += ", 🔋charging resumed after peak hours 🔌"
                    send_sms(notify_phone, msg)
                return 1

            elif response["result"] is False and response["reason"] == "requested":
                # This can happen if there was a voltage drop earlier and you can't restart it
                logger.error("Charging restart already requested")
                return None

            else:
                logger.error("Unrecognized response from Tessie API")
                return None

        else:
            logger.info("Leaving charging stopped during peak")
            return 0


if __name__ == "__main__":

    @click.command()
    @click.option("--vin", required=True, help="Tesla VIN number to auto vent", type=str)
    @click.option("--tessie-token", required=True, help="API access token for Tessie (see tessie.com)", type=str)
    @click.option("--peak-start", required=True, help="When peak pricing starts, in military time. Ex: 16:00", type=str)
    @click.option("--peak-end", required=True, help="When peak pricing ends, in military time. Ex: 21:00", type=str)
    @click.option(
        "--low-battery-threshold",
        default=DEFAULT_LOW_BATTERY_THRESHOLD,
        show_default=True,
        type=click.IntRange(0, 100),
        help="Don't pause charging if the battery is below this threshold",
    )
    @click.option(
        "--notify-phone", help="Send a message to this phone number when the charging is stopped/started", type=str
    )
    def peakoff_command(vin, tessie_token, peak_start, peak_end, notify_phone, low_battery_threshold):
        peakoff(vin, tessie_token, peak_start, peak_end, notify_phone, low_battery_threshold)

    peakoff_command()
