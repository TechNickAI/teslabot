from utils import c2f, f2c, get_sun_position
import arrow


def test_c2f():
    assert c2f(100) == 212
    assert c2f(33) == 91
    assert c2f(0) == 32
    assert c2f(-10) == 14


def test_f2c():
    assert f2c(212) == 100
    assert f2c(32) == 0
    assert f2c(88) == 31
    assert f2c(0) == -18
    assert f2c(-20) == -29


def test_sun_position():
    # San Francisco lat/long on September 8
    assert get_sun_position(37.7749, -122.4194, arrow.get("2022-09-08T03:15:17.568118-07:00")) == "night"
    assert get_sun_position(37.7749, -122.4194, arrow.get("2022-09-08T06:30:17.568118-07:00")) == "sunrise"
    assert get_sun_position(37.7749, -122.4194, arrow.get("2022-09-08T12:15:17.568118-07:00")) == "day"
    assert get_sun_position(37.7749, -122.4194, arrow.get("2022-09-08T19:45:17.568118-07:00")) == "sunset"
    assert get_sun_position(37.7749, -122.4194, arrow.get("2022-09-08T21:15:17.568118-07:00")) == "night"
