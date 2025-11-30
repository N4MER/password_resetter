import sys
import logging
import time
from re import Pattern

import serial
from serial.serialutil import SerialException

from utils.exceptions import StopBreakException, InterruptBootException, IncorrectResponseException
from utils.response_patterns import ResponsePatterns

LOG_LEVEL = logging.DEBUG

logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("serial_connection")

class SerialConnection:

    def __init__(self, port: str, baud_rate: int):
        self._port = port
        self._baud_rate = baud_rate
        self._connection = self.open_serial_connection()

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
            serial_connection = serial.Serial(port=self._port, baudrate=self._baud_rate)

            self._clear_buffer()

            logger.info("Opened serial port %s @ %d bps", self._port, self._baud_rate)

        except SerialException as e:
            logger.error("Failed to open serial port %s: %s", self._port, e)
            return None
        except Exception as e:
            logger.critical("Unexpected error during serial connection setup: %s", e)
            return None
        return serial_connection


    def read_output(self, clear_buffer: bool = True, read_timeout: float = 1) -> str:
        """
        Reads data from the serial connection.
        :param clear_buffer: If true, clears the buffer before reading.
        :param read_timeout: Reading stops if no new data is received from the device for this duration (default: 3s).
        :return: Read data from the serial connection.
        """
        logger.info(f"Starting Read from serial port {self._port}")

        if clear_buffer:
            self._clear_buffer()

        full_output = []
        read_amount = 4096

        last_data_time = time.time()

        while True:
            bytes_waiting = self._connection.in_waiting

            if bytes_waiting > 0:

                last_data_time = time.time()
                data_bytes = self._connection.read(min(bytes_waiting, read_amount))
                full_output.append(data_bytes)

            else:
                time_since_last_data = time.time() - last_data_time

                if time_since_last_data >= read_timeout:
                    logger.info("No data received for %s seconds, stopping read.", read_timeout)
                    break

                time.sleep(0.1)

        final_bytes = b"".join(full_output)
        return final_bytes.decode('utf-8', errors='ignore')


    def send(self, command: str, expected_response: Pattern[str] | None):
        """
        Sends data to the serial connection.
        :param command: Sent command.
        :param expected_response: Expected response.
        :return: True if the expected response matches.
        """

        self._clear_buffer()

        self._connection.write('\n'.encode())
        #self._connection.write(('end' + '\n').encode())

        logger.info(f"Sending command {command} to serial port {self._port}")
        self._connection.write((command + '\n').encode())

        output = self.read_output()

        if expected_response is not None:
            if not expected_response.search(output):
                raise IncorrectResponseException("Incorrect response received from serial port")

        logger.info(f"Successfully sent {command} to serial port {self._port}")


    def interrupt_boot(self, expected_response: Pattern[str] | None = ResponsePatterns.ROMMON):
        """
        Interrupts boot to enter ROMMON.
        :param expected_response: Expected ROMMON prompt.
        :return: True if entered ROMMON.
        """
        try:
            logger.info("Starting boot interrupt")
            self._clear_buffer()

            send_break_duration = 0.1

            while True:
                bytes_waiting = self._connection.in_waiting

                if bytes_waiting > 0:
                    break

                self._connection.send_break(send_break_duration)
                time.sleep(0.1)

            logger.info("Stopped sending break")
            output = self.read_output(False)

            if expected_response is not None:
                if not expected_response.search(output):
                    logger.error("Failed to interrupt boot")
                    raise InterruptBootException("Failed to interrupt boot")

        except StopBreakException:
            logger.info("Interrupt_boot stopped by user")
            raise InterruptBootException("Boot interrupt stopped by user")
        logger.info(f"Successfully interrupted boot")