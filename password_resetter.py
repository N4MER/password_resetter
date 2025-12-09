import logging
import sys

from utils.configuration_commands import ConfigurationCommands
from utils.response_patterns import ResponsePatterns

from serial_connection import SerialConnection

LOG_LEVEL = logging.DEBUG

logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("password_resetter")

class PasswordResetter:

    def __init__(self):
        self.remove_privileged_exec_mode_password = False
        self.remove_line_console_password = False
        self.encrypt_enable_password = False
        self.set_new_privileged_exec_mode_password = False
        self.set_new_line_console_password = False

        self._new_privileged_exec_mode_password = ""
        self._new_line_console_password = ""

    @property
    def new_privileged_exec_mode_password(self) -> str:
        return self._new_privileged_exec_mode_password

    @new_privileged_exec_mode_password.setter
    def new_privileged_exec_mode_password(self, new_privileged_exec_mode_password):
        if not new_privileged_exec_mode_password:
            raise ValueError("New privileged exec mode password cannot be Empty")
        if not isinstance(new_privileged_exec_mode_password, str):
            raise TypeError("New privileged exec mode password must be a string")

    @property
    def new_line_console_password(self) -> str:
        return self._new_line_console_password

    @new_line_console_password.setter
    def new_line_console_password(self, new_line_console_password):
        if not new_line_console_password:
            raise ValueError("New line console password cannot be Empty")
        if not isinstance(new_line_console_password, str):
            raise TypeError("New line console password must be a string")

    def reset_password(self, serial_connection: SerialConnection):
        logger.info("starting password reset")

        serial_connection.send(None, ResponsePatterns.ROMMON)
        serial_connection.send(ConfigurationCommands.ignore_startup_config, ResponsePatterns.ROMMON)
        logger.debug("Swapped startup config")
        serial_connection.send(ConfigurationCommands.reset_device, ResponsePatterns.INITIAL_SETUP_MESSAGE)
        logger.debug("Reloading device")

        serial_connection.send(ConfigurationCommands.no, ResponsePatterns.EXEC_MODE)
        logger.debug("Device reloaded")

        logger.debug("Entering privileged exec mode")
        serial_connection.send(ConfigurationCommands.enable, ResponsePatterns.EXEC_MODE)
        serial_connection.send(ConfigurationCommands.copy_startup_config_to_running_config, ResponsePatterns.EXEC_MODE)

        logger.debug("Copying startup config to running config")
        serial_connection.send(None, ResponsePatterns.EXEC_MODE)
        serial_connection.send(None, ResponsePatterns.EXEC_MODE)
        logger.debug("Startup config copyied to running config")

        logger.debug("Entering global configuration mode")
        serial_connection.send(ConfigurationCommands.enter_global_configuration_mode, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)

        if self.remove_privileged_exec_mode_password:
            logger.debug("Removing privileged exec mode password")
            serial_connection.send(ConfigurationCommands.remove_enable_password, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
            serial_connection.send(ConfigurationCommands.remove_enable_secret_password, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
            logger.info("Removed privileged exec mode password")

            if self.new_privileged_exec_mode_password:
                if self.encrypt_enable_password:
                    logger.debug("Setting new enable secret password")
                    serial_connection.send(ConfigurationCommands.set_enable_secret_password, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
                    logger.info("New enable secret password set")
                else:
                    logger.debug("Setting new enable password")
                    serial_connection.send(ConfigurationCommands.set_enable_password, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
                    logger.info("New enable password set")

        if self.remove_line_console_password:
            logger.debug("Removing line console password")
            serial_connection.send(ConfigurationCommands.enter_line_console, ResponsePatterns.LINE_CONFIGURATION_MODE)
            serial_connection.send(ConfigurationCommands.disable_login, ResponsePatterns.LINE_CONFIGURATION_MODE)
            serial_connection.send(ConfigurationCommands.remove_line_console_password, ResponsePatterns.LINE_CONFIGURATION_MODE)
            logger.info("Removed line console password")

            if self.new_line_console_password:
                logger.debug("Setting new line console password")
                serial_connection.send(ConfigurationCommands.set_line_console_password, ResponsePatterns.LINE_CONFIGURATION_MODE)
                serial_connection.send(ConfigurationCommands.enable_login, ResponsePatterns.LINE_CONFIGURATION_MODE)
                logger.info("New line console password set")

            serial_connection.send(ConfigurationCommands.exit, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
            logger.debug("Exited line console configuration mode")

        logger.info("Saving new configuration")
        serial_connection.send(ConfigurationCommands.reset_config_register_to_default, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
        serial_connection.send(ConfigurationCommands.end, None)
        serial_connection.send(None, ResponsePatterns.EXEC_MODE)
        logger.debug("Copying new running config to startup config")
        serial_connection.send(ConfigurationCommands.copy_running_config_to_startup_config, ResponsePatterns.EXEC_MODE)
        serial_connection.send(None, ResponsePatterns.EXEC_MODE)
        logger.info("New running config copied to startup config")
        logger.debug("Reloading device")
        serial_connection.send(ConfigurationCommands.reload, None)
        logger.info("Device reloaded")
        logger.info("Password reset finished")
