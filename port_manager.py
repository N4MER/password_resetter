import logging
import sys

import serial.tools.list_ports

LOG_LEVEL = logging.DEBUG

logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("port_manager")

class PortManager:

    @staticmethod
    def list_ports() -> list:
        """
        Lists all connected serial ports.
        :return: List of connected serial ports.
        """
        ports = serial.tools.list_ports.comports()
        logger.info("listing ports")
        return ports
