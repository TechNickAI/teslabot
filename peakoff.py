from loguru import logger
from Tessie import Tessie
from utils import send_sms
import arrow, click

DEFAULT_LOW_BATTERY_THRESHOLD = 42


def peakoff(vin, tessie_token, peak_start, peak_end, notify_phone, low_battery_threshold=DEFAULT_LOW_BATTERY_THRESHOLD):
    """

    Automatically stop charging during peak electricity hours

    """
    tessie = Tessie(tessie_token, vin)
    state = tessie.get_vehicle_state()
    car_name = state["display_name"]
    charge_state = state["charge_state"]
    msg = f"{car_name}🔋Battery level is {charge_state['battery_level']}% and is {charge_state['charging_state']}"
    logger.info(msg)
    car_time = tessie.get_car_time()
    logger.info(f"Car time is {car_time.format('HH:mm:ss')}")

    ### Conditional checks, all of these must pass to continue
    try:
        tessie.check_state(
            "drive_state",
            "timestamp",
            lambda v: arrow.get(v) > arrow.utcnow().shift(hours=-3),
            "API data is stale, which means the car is either asleep or out of internet range",
        )
        tessie.check_state("drive_state", "speed", lambda v: v is None or v == 0, "Car is driving 🛞")
        tessie.check_state("charge_state", "charge_port_door_open", lambda v: v, "Charge cable is not plugged in")
        tessie.check_state("charge_state", "charging_state", lambda v: v != "Complete", "Charging is complete ✅")
        tessie.check_state("charge_state", "charge_limit_soc", lambda v: v < 100, "User requested charging to 100%")
    except ValueError as e:
        logger.warning(f"🛑 Halting: {e}")
        return None

    ### Check the batteries and charging status
    car_time_24 = tessie.get_car_time().format("HH:mm")

    if charge_state["charging_state"] == "Charging":
        if charge_state["fast_charger_type"] == "Tesla":
            logger.success("Charging at a super charger 🔋")
            return 0

        if charge_state["fast_charger_type"] == "<invalid>":
            logger.success("Charging at a ChargePoint (or similar) 🔋")
            return 0

        if charge_state["battery_level"] < low_battery_threshold:
            logger.success(f"Charge level is below {low_battery_threshold}%, allowing charging to continue")
            return 0

        if car_time_24 > peak_start and car_time_24 < peak_end:
            logger.warning("Charging during peak time!")
            response = tessie.request("command/stop_charging", vin)
            logger.debug(f"Response {response}")
            if notify_phone:
                msg += f", charging paused during peak hours, will resume after {peak_end} ♻️"
                send_sms(notify_phone, msg)
            logger.success(msg)
            return -1
        else:
            logger.success("Leaving charging as is")
            return 0

    elif charge_state["charging_state"] == "Stopped":
        # Check to see if it is already charged enough
        if charge_state["battery_level"] >= charge_state["charge_limit_soc"] - 1:
            logger.success("Battery is already close to requested level, leave as is")
            return 0

        if car_time_24 > peak_end or car_time_24 < peak_start:
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
                return -2

            else:  # pragma: no cover
                logger.error(f"Unrecognized response from Tessie API: {response}")
                return -2

        else:
            logger.success("Leaving charging stopped during peak")
            return 0
    return None


### Set up the command line interface
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
def peakoff_command(vin, tessie_token, peak_start, peak_end, notify_phone, low_battery_threshold):  # pragma: no cover
    peakoff(vin, tessie_token, peak_start, peak_end, notify_phone, low_battery_threshold)


if __name__ == "__main__":  # pragma: no cover
    peakoff_command()  # pylint: disable=no-value-for-parameter
