from geopy import distance
from loguru import logger
from Tessie import Tessie
import click


def autosentry(vin, tessie_token, home_lat, home_long, radius):
    """

    Automatically set sentry mode when not at home

    """

    ### Setup
    tessie = Tessie(tessie_token, vin)
    state = tessie.get_vehicle_state()
    car_lat = state["drive_state"]["latitude"]
    car_long = state["drive_state"]["longitude"]
    sentry_mode = state["vehicle_state"]["sentry_mode"]
    msg = f'{state["display_name"]} is at {car_lat}, {car_long}, sentry mode is {sentry_mode}'
    logger.info(msg)

    ### Conditional checks, all of these must pass to continue
    try:
        tessie.check_state("vehicle_state", "is_user_present", lambda v: not v, "Someone is in the car 🙆")
        tessie.check_state("charge_state", "battery_level", lambda v: v > 25, "Battery level is low 🔋")
    except ValueError as e:
        logger.warning(f"🛑 Halting: {e}")
        return None

    distance_from_home = distance.distance((car_lat, car_long), (home_lat, home_long))
    if distance_from_home.feet > radius:
        logger.info(f"Car is {distance_from_home.miles} miles from home")
        if not sentry_mode:
            response = tessie.request("command/enable_sentry", vin)
            logger.success(f"Sentry enabled away from home: {response}")
        else:
            logger.success("Sentry already enabled away from home")
    else:
        logger.info("Car is home")
        if sentry_mode:
            response = tessie.request("command/disable_sentry", vin)
            logger.success(f"Sentry disabled at home: {response}")
        else:
            logger.success("Sentry already disabled at home")


### Set up the command line interface
@click.command()
@click.option("--vin", required=True, help="Tesla VIN number to auto vent", type=str)
@click.option("--tessie-token", required=True, help="API access token for Tessie (see tessie.com)", type=str)
@click.option("--home-lat", type=float, required=True)
@click.option("--home-long", type=float, required=True)
@click.option("--radius", type=int, help="How many feet away from home to trigger sentry mode", default=150)
def autosentry_command(vin, tessie_token, home_lat, home_long, radius):  # pragma: no cover
    autosentry(vin, tessie_token, home_lat, home_long, radius)


if __name__ == "__main__":  # pragma: no cover
    autosentry_command()
