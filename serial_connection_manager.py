import sys
import logging
import time
from re import Pattern

import serial
from serial.serialutil import SerialException

from utils.exceptions import IncorrectResponseException

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("serial_connection")

class SerialConnectionManager:

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


    def open_serial_connection(self):
        """
        Open a serial connection.
        """
        try:
            self._connection = serial.Serial(port=self._port, baudrate=self._baud_rate)

            self._clear_buffer()

            logger.info("Opened serial port %s @ %d bps", self._port, self._baud_rate)

        except SerialException as e:
            raise SerialException(e)
        except Exception as e:
            raise Exception(e)

    def read_output(self, read_timeout: float = 5):
        """
        Read output from  serial connection until no output read for the duration of read_timeout.
        :param read_timeout: Read timeout.
        :return: Read output.
        """
        logger.info(f"Starting Read from serial port {self._port}")

        output = ""
        read_amount = 4096

        last_data_time = time.time()

        while True:
            bytes_waiting = self._connection.in_waiting

            if bytes_waiting > 0:

                last_data_time = time.time()
                data_bytes = self._connection.read(min(bytes_waiting, read_amount))
                output += data_bytes.decode('utf-8', errors='ignore')

            else:
                time_since_last_data = time.time() - last_data_time

                if time_since_last_data >= read_timeout:
                    logger.info("No data received for %s seconds, stopping read.", read_timeout)
                    break

                time.sleep(0.1)
        logger.info("stopped read")
        return output

    def read_until_expected_output(self, expected_response: Pattern[str], read_timeout: float = 5) -> bool:
        """
        Reads output from the serial connection until there is no data read for the duration of read_timeout or until the expected response is received.
        :param expected_response: Expected response.
        :param read_timeout: Reading stops if no new data is received from the device for this duration (default: 5s).
        :return: True if the expected response matches.
        """
        logger.info(f"Starting Read from serial port {self._port}")

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



    def send_command(self, command: str | None = None, expected_response: Pattern[str] | None = None, read_timeout: float = 5):
        """
        Sends data to the serial connection and checks if output matches the expected_response regex.
        :param read_timeout: Read timeout.
        :param command: Sent command.
        :param expected_response: Expected response.
        :return: True if the expected response matches.
        """

        self._clear_buffer()

        command_to_send = command if command is not None else ""

        logger.info(f"Sending command {command} to serial port {self._port}")

        self._connection.write((command_to_send + '\n').encode())

        if expected_response is not None:
            is_response_correct = self.read_until_expected_output(expected_response, read_timeout)

            if not is_response_correct:
                raise IncorrectResponseException("Incorrect response received from serial port.")


        logger.info(f"Successfully sent {command} to serial port {self._port}")


    def close_connection(self):
        """
        Close the serial connection.
        :return:
        """
        self._connection.close()

    def check_mode(self):
        """
        Sends an empty command to the serial connection then reads and returns the output.
        :return: Output from sending empty command.
        """
        self._connection.write(b'\n')
        time.sleep(0.1)
        mode = self.read_output(1.0)
        return mode