import logging
import sys

from utils.cisco_devices import Device, BootEnvironment
from utils.configuration_commands import Commands, ROMMONCommands, SwitchBootloaderCommands
from utils.response_patterns import ResponsePatterns

from serial_connection_manager import SerialConnectionManager

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
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

    def reset_password(self, serial_connection_manager: SerialConnectionManager, device: Device):
        logger.info("starting password reset")

        PasswordResetter.ignore_startup_config(serial_connection_manager, device)

        logger.debug("Entering global configuration mode")
        serial_connection_manager.send_command(Commands.enter_global_configuration_mode, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)

        if self.remove_privileged_exec_mode_password:
            logger.debug("Removing privileged exec mode password")
            serial_connection_manager.send_command(Commands.remove_enable_password, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
            serial_connection_manager.send_command(Commands.remove_enable_secret_password, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
            logger.info("Removed privileged exec mode password")

            if self.new_privileged_exec_mode_password:
                if self.encrypt_enable_password:
                    logger.debug("Setting new enable secret password")
                    new_enable_secret_password = Commands.set_enable_secret_password
                    new_enable_secret_password.format(password=self._new_privileged_exec_mode_password)
                    serial_connection_manager.send_command(new_enable_secret_password, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
                    logger.info("New enable secret password set")

                else:
                    logger.debug("Setting new enable password")
                    new_enable_password_command = Commands.set_enable_password
                    new_enable_password_command.format(password=self._new_privileged_exec_mode_password)
                    serial_connection_manager.send_command(new_enable_password_command, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
                    logger.info("New enable password set")

        if self.remove_line_console_password:
            logger.debug("Removing line console password")
            serial_connection_manager.send_command(Commands.enter_line_console, ResponsePatterns.LINE_CONFIGURATION_MODE)
            serial_connection_manager.send_command(Commands.disable_login, ResponsePatterns.LINE_CONFIGURATION_MODE)
            serial_connection_manager.send_command(Commands.remove_line_console_password, ResponsePatterns.LINE_CONFIGURATION_MODE)
            logger.info("Removed line console password")

            if self.new_line_console_password:
                logger.debug("Setting new line console password")
                new_line_console_password = Commands.set_line_console_password
                new_line_console_password.format(password=self._new_line_console_password)
                serial_connection_manager.send_command(Commands.set_line_console_password, ResponsePatterns.LINE_CONFIGURATION_MODE)
                serial_connection_manager.send_command(Commands.enable_login, ResponsePatterns.LINE_CONFIGURATION_MODE)
                logger.info("New line console password set")

            serial_connection_manager.send_command(Commands.exit, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
            logger.debug("Exited line console configuration mode")

        logger.info("Saving new configuration")

        PasswordResetter.finish_reset(serial_connection_manager, device)

        serial_connection_manager.send_command(Commands.end, None)
        serial_connection_manager.send_command(None, ResponsePatterns.PRIVILEGED_EXEC_MODE)
        logger.debug("Copying new running config to startup config")
        serial_connection_manager.send_command(Commands.copy_running_config_to_startup_config, ResponsePatterns.DESTINATION_FILE_RENAME)
        serial_connection_manager.send_command(None, ResponsePatterns.PRIVILEGED_EXEC_MODE)
        logger.info("New running config copied to startup config")
        logger.debug("Reloading device")
        serial_connection_manager.send_command(Commands.reload, ResponsePatterns.PROCEED_WITH_RELOAD)
        serial_connection_manager.send_command(None, None)
        logger.info("Device reloaded")
        logger.info("Password reset finished")

        serial_connection_manager.close_connection()

    @staticmethod
    def ignore_startup_config(serial_connection_manager: SerialConnectionManager, device: Device):

        if device.boot_environment == BootEnvironment.ROMMON:
            serial_connection_manager.send_command(None, ResponsePatterns.ROMMON)
            serial_connection_manager.send_command(ROMMONCommands.ignore_startup_config, ResponsePatterns.ROMMON)
            logger.debug("Swapped startup config")
            logger.debug("Reloading device")
            serial_connection_manager.send_command(ROMMONCommands.reload, ResponsePatterns.INITIAL_SETUP_MESSAGE, 10)
            serial_connection_manager.send_command(Commands.no, ResponsePatterns.EXEC_MODE)
            logger.debug("Device reloaded")
            logger.debug("Entering privileged exec mode")
            serial_connection_manager.send_command(Commands.enable, ResponsePatterns.PRIVILEGED_EXEC_MODE)
            logger.debug("Copying startup config to running config")
            serial_connection_manager.send_command(Commands.copy_startup_config_to_running_config, ResponsePatterns.DESTINATION_FILE_RENAME)
            serial_connection_manager.send_command(None, ResponsePatterns.PRIVILEGED_EXEC_MODE, 10)
            logger.debug("Startup config copied to running config")

        elif device.boot_environment == BootEnvironment.SWITCH_BOOTLOADER:
            serial_connection_manager.send_command(None, ResponsePatterns.BOOTLOADER)
            serial_connection_manager.send_command(SwitchBootloaderCommands.initialize_flash, ResponsePatterns.BOOTLOADER)
            serial_connection_manager.send_command(SwitchBootloaderCommands.rename_startup_config, ResponsePatterns.BOOTLOADER)
            logger.debug("Renamed config.txt")
            logger.debug("Rebooting device")
            serial_connection_manager.send_command(SwitchBootloaderCommands.boot, ResponsePatterns.EXEC_MODE, 10)
            serial_connection_manager.send_command(Commands.no, ResponsePatterns.EXEC_MODE)
            logger.debug("Device rebooted")
            serial_connection_manager.send_command(Commands.enable, ResponsePatterns.PRIVILEGED_EXEC_MODE)
            logger.debug("Copying old startup config to running config")
            serial_connection_manager.send_command(Commands.rename_startup_config_to_default, ResponsePatterns.DESTINATION_FILE_RENAME)
            serial_connection_manager.send_command(None, ResponsePatterns.PRIVILEGED_EXEC_MODE)
            serial_connection_manager.send_command(Commands.copy_config_file_to_running_config, ResponsePatterns.DESTINATION_FILE_RENAME)
            serial_connection_manager.send_command(None, ResponsePatterns.PRIVILEGED_EXEC_MODE, 10)


    @staticmethod
    def finish_reset(serial_connection_manager: SerialConnectionManager, device: Device):

        if device.boot_environment == BootEnvironment.ROMMON:
            serial_connection_manager.send_command(Commands.reset_config_register_to_default, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
