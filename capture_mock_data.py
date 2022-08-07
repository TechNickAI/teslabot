import json

import click
from loguru import logger

from Tessie import Tessie


@click.command()
@click.option("--label", required=True, help="Tesla VIN number to auto vent")
@click.option("--vin", required=True, help="Tesla VIN number to auto vent")
@click.option("--tessie_token", required=True, help="API access token for Tessie (see tessie.com)")
def capture(tessie_token, vin, label):
    tessie = Tessie(tessie_token, vin)
    result = tessie.get_vehicles()

    f = open(f"tests/mock_data/{label}.json", "w")
    f.write(json.dumps(result, indent=4))

    logger.success(f"Data written for {label}")


if __name__ == "__main__":
    capture()
