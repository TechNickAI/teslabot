from loguru import logger
from Tessie import Tessie
from utils import c2f, send_sms
import arrow, click


def autovent(vin, tessie_token, vent_temp, notify_phone):
    """

    Automatically vent the windows to lower cabin temperature

    """

    tessie = Tessie(tessie_token, vin)
    state = tessie.get_vehicle_state()
    car_name = state["display_name"]
    climate_state = state["climate_state"]
    vehicle_state = state["vehicle_state"]
    logger.trace(f"Climate state: {climate_state}")
    logger.trace(f"Vehicle state: {vehicle_state}")

    inside_temp = c2f(climate_state["inside_temp"])
    outside_temp = c2f(climate_state["outside_temp"])

    ### Conditional checks
    if tessie.localize_time(arrow.utcnow().shift(hours=-3)) > tessie.localize_time(
        arrow.get(state["drive_state"]["timestamp"])
    ):
        logger.info("API data is stale, which means the car is either asleep or out of internet range.")
        if int(tessie.localize_time(arrow.utcnow())) <= 6:
            logger.info("Since it's before sunrise, just let the car sleep")
        else:
            logger.info("Waking the car up for the next run")
            tessie.wake_up()

        return None

    try:
        tessie.check_state("drive_state", "speed", lambda v: v is None, "Car is driving 🛞")
        tessie.check_state("vehicle_state", "is_user_present", lambda v: not v, "Someone is in the car 🙆")
    except ValueError as e:
        logger.info(f"Halting: {e}")
        return None

    ### Check the temperature and windows
    msg = f"{car_name} cabin temperature is {inside_temp}° and outside temperature is {outside_temp}°"
    logger.info(msg)

    if vehicle_state["rd_window"] != 0:
        logger.info("Windows are down")
        if inside_temp < vent_temp:
            tessie.wake_up()
            response = tessie.request("command/close_windows", vin)
            logger.success(f"Windows closed: {response}")
            if notify_phone:
                msg += ", windows rolled up 🔒"
                send_sms(notify_phone, msg)
            return 1
        else:
            logger.info("Leaving windows as is")
            return 0

    else:
        logger.info("Windows are up")
        if inside_temp > vent_temp and outside_temp < inside_temp:
            tessie.wake_up()
            response = tessie.request("command/vent_windows", vin)
            logger.success(f"Windows vented: {response}")
            if notify_phone:
                msg += " 🥵, windows vented to cool off 🌬"
                send_sms(notify_phone, msg)
            return -1
        else:
            logger.info("Leaving windows as is")
            return 0


@click.command()
@click.option("--vin", required=True, help="Tesla VIN number to auto vent", type=str)
@click.option("--tessie-token", required=True, help="API access token for Tessie (see tessie.com)", type=str)
@click.option(
    "--vent-temp",
    default=70,
    type=click.IntRange(0, 135),
    show_default=True,
    help="The threshold for when to roll up/down the windows, degrees in fahrenheit",
)
@click.option("--notify-phone", help="Send a message to this phone number when the windows are moved", type=str)
def autovent_command(vin, tessie_token, vent_temp, notify_phone):
    autovent(vin, tessie_token, vent_temp, notify_phone)


if __name__ == "__main__":  # pragma: no cover
    autovent_command()
