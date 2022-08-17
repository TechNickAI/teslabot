import os

from loguru import logger
from twilio.rest import Client


def c2f(celsius):
    return round((celsius * 9 / 5) + 32)


def f2c(fahrenheit):
    return (fahrenheit - 32) * 5 / 9


def send_sms(phone, message):
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    twilio_phone = os.environ["TWILIO_PHONE"]
    assert account_sid, "TWILIO_ACCOUNT_SID env variable must be set"
    assert auth_token, "TWILIO_AUTH_TOKEN env variable must be set"
    assert twilio_phone, "TWILIO_PHONE env variable must be set"
    client = Client(account_sid, auth_token)
    logger.info(f"Sending message to {phone}: {message}")
    message = client.messages.create(body=f"Tesla 🤖: {message}", from_=f"+{twilio_phone}", to=f"+{phone}")
    return message.sid
