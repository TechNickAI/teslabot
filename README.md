# TeslaBot 🤖

Automating functionality for Tesla, using the same API the app uses via [Tessie](https://tessie.com/)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


## Auto Venting
It's hot out. Sun is streaming in. Interior temperatures can exceed 100°F, damaging the cars interior and making it uncomfortable when you get in. Tesla has a feature to cool down the cabin when it gets hot, but this uses up battery.

Yes, you can open the app to vent, but it's not ideal to have to remember to do it every time you park. It's also nice to only vent the windows when it is hot, not all the time.

autovent solves this by allowing you to set a threshold for venting

```
Usage: autovent.py [OPTIONS]

  Automatically vent the windows to lower cabin temperature

Options:
  --vin TEXT           Tesla VIN number to auto vent  [required]
  --tessie_token TEXT  API access token for Tessie (see tessie.com)
                       [required]
  --vent_temp INTEGER  The threshold for when to roll up/down the windows,
                       degrees in farenheit
  --notify_phone TEXT  Send a message to this phone number when the windows
                       are moved
  --help               Show this message and exit.
```

## Off peak charging

Tesla's native off-peak scheduling sucks. It allows you to specify a "start time", but no end time, when in practicality you need to be able to specify a peak window, such as 4-9PM for PG&E in Northern California, and have the charging stop during this window.


```
Usage: peakoff.py [OPTIONS]

Options:
  --vin TEXT                      Tesla VIN number to auto vent  [required]
  --tessie_token TEXT             API access token for Tessie (see tessie.com)
                                  [required]
  --peak-start TEXT               When peak pricing starts, in military time.
                                  Ex: 16:00  [required]
  --peak-end TEXT                 When peak pricing ends, in military time.
                                  Ex: 21:00  [required]
  --low_battery_threshold INTEGER
                                  Don't pause charging if the battery is below
                                  this threshold  [default: 35]
  --notify_phone TEXT             Send a message to this phone number when the
                                  charging is stopped/started
  --help                          Show this message and exit.
```
