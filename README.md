# TeslaBot 🤖

Automating functionality for Tesla, using the same API the app uses via [Tessie](https://tessie.com/)

[![Github Build](https://github.com/gorillamania/teslabot/actions/workflows/build.yml/badge.svg)](https://github.com/gorillamania/teslabot/actions?query=build)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![GitHub Super-Linter](https://github.com/gorillamania/teslabot/workflows/Lint%20Code%20Base/badge.svg)](https://github.com/marketplace/actions/super-linter)
[![codecov](https://codecov.io/gh/gorillamania/teslabot/branch/master/graph/badge.svg?token=MPHAFA1QX9)](https://codecov.io/gh/gorillamania/teslabot)


Various automations can be performed based on time of day, location of the vehicle, and conditions of the car. Have an idea for a feature? [Submit a GitHub issue](https://github.com/gorillamania/teslabot/issues/new) to suggest a feature.

Optional SMS notifications available via [Twilio](https://www.twilio.com/).

<img width="524" alt="Screen Shot 2022-08-12 at 1 40 17 PM" src="https://user-images.githubusercontent.com/142708/184441792-82dbea01-bb19-418f-ae89-b6d843aa3489.png">


## Features

### Auto Venting
It's hot out. Sun is streaming in. Interior temperatures can exceed 100°F, damaging the cars interior and making it uncomfortable when you get in. Tesla has a feature to cool down the cabin when it gets hot, but this uses up battery.

Yes, you can open the app to vent, but it's not ideal to have to remember to do it every time you park. It's also nice to only vent the windows when it is hot, not all the time.

autovent solves this by allowing you to set a threshold for venting

```text
Usage: autovent.py [OPTIONS]

Options:
  --vin TEXT                 Tesla VIN number to auto vent  [required]
  --tessie-token TEXT        API access token for Tessie (see tessie.com)
                             [required]
  --vent-temp INTEGER RANGE  The threshold for when to roll up/down the
                             windows, degrees in fahrenheit  [default: 70;
                             0<=x<=135]
  --notify-phone TEXT        Send a message to this phone number when the
                             windows are moved
  --help                     Show this message and exit.
```

### Off peak charging

Tesla's native off-peak scheduling sucks. It allows you to specify a "start time", but no end time, when in practicality you need to be able to specify a peak window, such as 4-9PM for PG&E in Northern California, and have the charging stop during this window.


```text
Usage: peakoff.py [OPTIONS]

Options:
  --vin TEXT                      Tesla VIN number to auto vent  [required]
  --tessie-token TEXT             API access token for Tessie (see tessie.com)
                                  [required]
  --peak-start TEXT               When peak pricing starts, in military time.
                                  Ex: 16:00  [required]
  --peak-end TEXT                 When peak pricing ends, in military time.
                                  Ex: 21:00  [required]
  --low-battery-threshold INTEGER RANGE
                                  Don't pause charging if the battery is below
                                  this threshold  [default: 42; 0<=x<=100]
  --notify-phone TEXT             Send a message to this phone number when the
                                  charging is stopped/started
  --help                          Show this message and exit.
```



## Development Environment

* Python 3.9+ w/ virtualenv
* [GitHub actions](https://github.com/features/actions) for CI/CD
* [Super Linter](https://github.com/marketplace/actions/super-linter) for linting, including: 
    * [Black](https://black.readthedocs.io/en/stable/) for perfect python formatting
    * [flake8](https://flake8.pycqa.org/en/latest/) for python linting
    * [isort](https://pypi.org/project/isort/) for consistent imports
* [pytest](https://docs.pytest.org/en/7.1.x/) for unit testing
* [pre-commit](https://pre-commit.com/) to automate checks on commit

`pip install -r requirements.txt` for production, [requirements-test.txt](requirements-test.txt) for testing/CI/CD, and [requirements-dev.txt](requirements-dev.txt) for local development. 
