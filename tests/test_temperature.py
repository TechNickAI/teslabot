from utils import c2f, f2c


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
