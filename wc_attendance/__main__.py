import logging
import argparse
import time
from typing import Generator

from .data_store import DataStore, CardUid
from .json_store import JsonFileStore
from .nfc import Nfc


def setup_logging():
    # Set up logging
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    fm = logging.Formatter(
        "%(asctime)s - %(name)-25s - %(funcName)-10s - %(levelname)-5s"
        + " - %(message)s")
    ch.setFormatter(fm)
    root.addHandler(ch)


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Wireless Club RFID Attendance")
    subparsers = parser.add_subparsers(help="Attendance Modes")
    att = subparsers.add_parser("attendance", help="Log attendance")
    att.set_defaults(func=mode_log_attendance)
    reg = subparsers.add_parser("register", help="Register new people")
    reg.set_defaults(func=mode_register_people)
    return parser


def unique_card_generator(nfc: Nfc) -> Generator[CardUid, None, None]:
    try:
        last_cards = set()
        while True:
            curr_cards = nfc.poll_uids()
            diff_cards = curr_cards - last_cards
            last_cards = last_cards & curr_cards
            for uid in diff_cards:
                yield uid
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt - exiting")


def mode_log_attendance(data_store: DataStore, nfc: Nfc) -> None:
    logger.info("Begin logging attendance")

    for uid in unique_card_generator(nfc):
        owner = data_store.find_person_by_card(uid)
        if owner is None:
            logger.warning("No person found with card %x", uid)
        else:
            owner.log_attendance()
            logger.info("Attendance logged for %s", owner.get_name())


def mode_register_people(data_store: DataStore, nfc: Nfc) -> None:
    logger.info("Begin registering people")

    for uid in unique_card_generator(nfc):
        owner = data_store.find_person_by_card(uid)
        if owner is not None:
            logger.warning("Person with card %x already exists: %s",
                           uid, owner.get_name())
        else:
            logger.info("Registering new person for card %x", uid)
            name = input("Enter your name: ")
            person = data_store.new_person(name)
            person.register_card(uid)
            person.log_attendance()
            logger.info(
                "Success - registered %s and logged attendance",
                name)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = setup_parser()
    args = parser.parse_args()
    if 'func' not in args:
        parser.print_help()
        raise SystemExit()

    try:
        logger.info("Starting attendance")
        with Nfc() as nfc:
            devices = nfc.get_devices()
            logger.info("Found nfc devices %s", devices)
            if len(devices) == 0:
                logger.error("No nfc devices found")
                raise SystemExit()
            logger.info("Using reader %s", devices[0])
            nfc.select_device(devices[0])

            data_store = JsonFileStore()
            args.func(data_store, nfc)
    except Exception:
        logger.exception("Ran into error")
