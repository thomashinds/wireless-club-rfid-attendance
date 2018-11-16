# Wireless Club RFID Attendance #

RFID attendance tracking system for NEU Wireless Club.

## Install ##

```bash
$ apt install libnfc libfreefare
$ pip install --user -e .
```

## Usage ##

Run attendance tracking:

```bash
$ wc-attendance
```

Yellow LED: New card detected, person must enter their name to be added to the system
Green LED: Success, attendance was logged

Data gets stored in `~/attendance.json`

## Development Usage ##

For development/testing, run from repo directory:

```bash
$ python3 -m wc_attendance
```
