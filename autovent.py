from loguru import logger
from Tessie import Tessie
from utils import c2f, get_sun_position, send_sms
import arrow, click


def autovent(vin, tessie_token, vent_temp, notify_phone):
    """

    Automatically vent the windows to lower cabin temperature

    """

    ### Setup
    tessie = Tessie(tessie_token, vin)
    state = tessie.get_vehicle_state()
    car_name = state["display_name"]
    climate_state = state["climate_state"]
    drive_state = state["drive_state"]
    inside_temp = c2f(climate_state["inside_temp"])
    outside_temp = c2f(climate_state["outside_temp"])
    car_time = tessie.get_car_time()
    sun_position = get_sun_position(drive_state["latitude"], drive_state["longitude"], car_time)
    logger.info(f"Car time is {car_time.format('HH:mm:ss')}, sun position is {sun_position}")
    msg = f"{car_name} cabin temp is {inside_temp}°, outside temp is {outside_temp}°, threshold is {vent_temp}°"
    logger.info(msg)

    ### Handle if the data is stale, which can happen if the car is out of internet range or asleep
    if arrow.get(drive_state["timestamp"]) < arrow.utcnow().shift(hours=-3):
        logger.info("API data is stale, which means the car is either asleep or out of internet range.")
        if sun_position in ["night", "sunrise"] and not tessie.are_windows_open():
            logger.success(f"Since it's {sun_position} and the windows are closed, just let the car sleep")
            return 11
        elif state["charge_state"]["battery_level"] < 25:
            logger.warning(f"Don't wake the car up, it's low on battery ({state['charge_state']['battery_level']}%)")
            return 12
        else:
            logger.success("Waking the car up for the next run of autovent")
            tessie.wake_up()
            return 13

    ### Conditional checks, all of these must pass to continue
    try:
        tessie.check_state("drive_state", "speed", lambda v: v is None, "Car is driving 🛞")
        tessie.check_state("vehicle_state", "is_user_present", lambda v: not v, "Someone is in the car 🙆")
    except ValueError as e:
        logger.warning(f"🛑 Halting: {e}")
        return None

    ### Now check the temperature and windows, and vent/close if needed
    if tessie.are_windows_open():
        logger.info("Windows are open")
        if inside_temp < vent_temp:
            tessie.wake_up()
            response = tessie.request("command/close_windows", vin)
            logger.success(f"Windows closed: {response}")
            if notify_phone:
                msg += ", windows rolled up 🔒"
                send_sms(notify_phone, msg)
            return 1
        else:
            logger.success("Leaving windows vented")
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
            logger.success("Leaving windows up")
            return 0


### Set up the command line interface
@click.command()
@click.option("--vin", required=True, help="Tesla VIN number to auto vent", type=str)
@click.option("--tessie-token", required=True, help="API access token for Tessie (see tessie.com)", type=str)
@click.option(
    "--vent-temp",
    default=85,
    type=click.IntRange(0, 135),
    show_default=True,
    help="The threshold for when to roll up/down the windows, degrees in fahrenheit",
)
@click.option("--notify-phone", help="Send a message to this phone number when the windows are moved", type=str)
def autovent_command(vin, tessie_token, vent_temp, notify_phone):  # pragma: no cover
    autovent(vin, tessie_token, vent_temp, notify_phone)


if __name__ == "__main__":  # pragma: no cover
    autovent_command()  # pylint: disable=no-value-for-parameter
