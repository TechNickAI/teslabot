from astral import LocationInfo
from astral.sun import sun
from loguru import logger
from twilio.rest import Client
import os


def c2f(celsius: float) -> int:
    return round(celsius * 9 / 5 + 32)


def f2c(fahrenheit: float) -> int:
    return round((fahrenheit - 32) * 5 / 9)


def send_sms(phone: str, message: str):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_phone = os.environ.get("TWILIO_PHONE")
    assert account_sid, "TWILIO_ACCOUNT_SID env variable must be set"
    assert auth_token, "TWILIO_AUTH_TOKEN env variable must be set"
    assert twilio_phone, "TWILIO_PHONE env variable must be set"

    client = Client(account_sid, auth_token)
    logger.info(f"Sending message to {phone}: {message}")
    message = client.messages.create(body=f"Tesla 🤖: {message}", from_=f"+{twilio_phone}", to=f"+{phone}")
    return message.sid


def get_sun_position(latitude, longitude, time):
    # Calculate the sun position for the supplied latitude, longitude, and time
    city = LocationInfo("City", "State", "US", latitude, longitude)
    astral = sun(city.observer, date=time.date(), tzinfo=time.tzinfo)
    if time < astral["dawn"] or time > astral["dusk"]:
        return "night"
    elif time > astral["dawn"] and time < astral["sunrise"]:
        return "sunrise"
    elif time > astral["sunrise"] and time < astral["sunset"]:
        return "day"
    elif time > astral["sunset"] and time < astral["dusk"]:
        return "sunset"
    else:  # pragma: no cover
        # not sure how we'd get here, but just in case
        raise ValueError("Unexpected time")
