from Tessie import Tessie
import click
from utils import c2f
from loguru import logger


@click.command()
@click.option("--vin", help="Tesla VIN number to auto vent")
@click.option("--tessie_token", help="API access token for Tessie (see tessie.com)")
@click.option("--vent_temp", default=70, help="The threshold for when to roll up/down the windows, degrees in farenheit")
def autovent(vin, tessie_token, vent_temp):
    """
    Automatically vent the windows to lower cabin temperature


    """
    tessie = Tessie(tessie_token)
    state = tessie.get_vehicle_state(vin)
    climate_state = state["climate_state"]
    vehicle_state = state["vehicle_state"]
    logger.debug(f"Climate state: {climate_state}")
    logger.debug(f"Vehicle state: {vehicle_state}")

    inside_temp = c2f(climate_state["inside_temp"])
    outside_temp = c2f(climate_state["outside_temp"])

    if state["drive_state"]["speed"] is not None:
        logger.warning("Car is driving, exiting")
        return

    logger.info(f"Inside temperature is {inside_temp}° and outside temperature is {outside_temp}°")

    if vehicle_state["rd_window"] != 0:
        logger.info("Windows are down")
        if inside_temp < vent_temp:
            tessie.request("command/close_windows", vin)
            logger.success("Windows closed")
        else:
            logger.info("Leaving windows as is")
    else:
        logger.info("Windows are up")
        if inside_temp > vent_temp and outside_temp < inside_temp:
            tessie.request("command/vent_windows", vin)
            logger.success("Windows vented")
        else:
            logger.info("Leaving windows as is")


if __name__ == "__main__":
    autovent()
