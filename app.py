"""
Startup app for the Router Service.
"""
import logging
import os

from src.router_service import router_service
from src.router_service.services.generate_and_pickle import generate_and_pickle, estimate_memory_impact

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

if __name__ == "__main__":
    logging.info("Starting Router Service")
    logging.info("Log Level: %s", logging.getLevelName(logging.getLogger().getEffectiveLevel()))
    if os.environ.get("PICKLE") == "1":
        logging.info("Staring in  generate mode")
        generate_and_pickle()
    elif os.environ.get("TEST_MEMSIZE") == "1":
        logging.info("Staring in memory estimation mode")
        estimate_memory_impact()
    else:
        logging.info("Starting in router mode")
        router_service.run()
