import logging
import os

from src.router_service import router_service

match os.environ.get("LOG_LEVEL"):
    case "DEBUG":
        logging.getLogger().setLevel(logging.DEBUG)
    case "INFO":
        logging.getLogger().setLevel(logging.INFO)
    case "WARNING":
        logging.getLogger().setLevel(logging.WARNING)
    case "ERROR":
        logging.getLogger().setLevel(logging.ERROR)
    case _:
        logging.getLogger().setLevel(logging.WARNING)
router_service.run()
