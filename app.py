import logging

from src.router_service import router_service

logging.getLogger().setLevel(logging.WARNING)
router_service.run()
