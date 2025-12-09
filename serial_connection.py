import sys
import logging
import time
from re import Pattern

import serial
from serial.serialutil import SerialException

from utils.exceptions import IncorrectResponseException

LOG_LEVEL = logging.DEBUG

logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("serial_connection")

class SerialConnection:

    def __init__(self):
        self._port = None
        self._baud_rate = None
        self._connection = None

    @property
    def connection(self) -> serial.Serial:
        return self._connection

    @connection.setter
    def connection(self, connection: serial.Serial):
        self._connection = connection

    @property
    def port(self) -> str | None:
        return self._port

    @port.setter
    def port(self, port: str | None):
        self._port = port

    @property
    def baud_rate(self) -> int:
        return self._baud_rate

    @baud_rate.setter
    def baud_rate(self, baud_rate: int):
        self._baud_rate = baud_rate

    def _clear_buffer(self):
        """
        Clears the buffer of the serial connection.
        :return:
        """
        self._connection.reset_input_buffer()
        self._connection.reset_output_buffer()


    def open_serial_connection(self) -> serial.Serial | None:
        """
        Open a serial connection.
        :return: The serial connection.
        """
        try:
            self._connection = serial.Serial(port=self._port, baudrate=self._baud_rate)

            self._clear_buffer()

            logger.info("Opened serial port %s @ %d bps", self._port, self._baud_rate)

        except SerialException as e:
            logger.error("Failed to open serial port %s: %s", self._port, e)
            return None
        except Exception as e:
            logger.critical("Unexpected error during serial connection setup: %s", e)
            return None


    def read_until_expected_output(self, expected_response: Pattern[str], read_timeout: float = 5, clear_buffer: bool = True) -> bool:
        """
        Reads data from the serial connection until there is no data read for the duration of read_timeout or until the expected response is received.
        :param expected_response: Expected response.
        :param clear_buffer: If true, clears the buffer before reading.
        :param read_timeout: Reading stops if no new data is received from the device for this duration (default: 3s).
        :return: True if the expected response matches.
        """
        logger.info(f"Starting Read from serial port {self._port}")

        if clear_buffer:
            self._clear_buffer()

        output = ""
        read_amount = 4096

        last_data_time = time.time()

        while True:
            bytes_waiting = self._connection.in_waiting

            if bytes_waiting > 0:

                last_data_time = time.time()
                data_bytes = self._connection.read(min(bytes_waiting, read_amount))
                output += data_bytes.decode('utf-8', errors='ignore')

                if expected_response.search(output):
                    return True

            else:
                time_since_last_data = time.time() - last_data_time

                if time_since_last_data >= read_timeout:
                    logger.info("No data received for %s seconds, stopping read.", read_timeout)
                    break

                time.sleep(0.1)
        logger.info("stopped read")
        return False


    def send(self, command: str | None = None, expected_response: Pattern[str] | None = None):
        """
        Sends data to the serial connection.
        :param command: Sent command.
        :param expected_response: Expected response.
        :return: True if the expected response matches.
        """

        self._clear_buffer()

        command_to_send = command if command is not None else ""

        logger.info(f"Sending command {command} to serial port {self._port}")

        self._connection.write((command_to_send + '\n').encode())

        is_response_correct = self.read_until_expected_output(expected_response)

        if not is_response_correct:
            raise IncorrectResponseException("Incorrect response received from serial port.")

        logger.info(f"Successfully sent {command} to serial port {self._port}")

    def close_connection(self):
        """
        Close the serial connection.
        :return:
        """
        self._connection.close()