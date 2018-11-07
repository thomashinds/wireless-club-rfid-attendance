import logging


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


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    from .json_store import JsonFileStore

    try:
        logger.info("Test")
        store = JsonFileStore()
        p = store.find_person_by_card(0x12345678)
        if p is None:
            p = store.new_person("John Smith")
            p.register_card(0x12345678)
        p.log_attendance()
    except Exception:
        logger.exception("Ran into error")
