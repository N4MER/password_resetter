import logging
import sys

from PyQt5.QtCore import QThread, QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from UI.ui_main_window import Ui_MainWindow
from password_resetter import PasswordResetter
from serial_connection_manager import SerialConnectionManager
from utils.cisco_devices import Devices
from utils.exceptions import SelectionError

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("port_manager")

class PasswordResetWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, serial_manager, password_resetter, device):
        super().__init__()
        self.serial_manager = serial_manager
        self.password_resetter = password_resetter
        self.device = device

    def run(self):
        try:
            self.password_resetter.reset_password(self.serial_manager, self.device)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._serial_connection_manager = SerialConnectionManager()
        self._password_resetter = PasswordResetter()
        self.setWindowTitle("Cisco Password Reset Tool")
        self.initialize()
        self._resetting_password = False

    def load_device_list(self):
        for device in Devices.devices:
            self.device_selector.addItem(device.model)

    def find_device(self):
        for device in Devices.devices:
            if device.model == self.device_selector.currentText():
                return device
        raise SelectionError("Please select a valid device")

    def initialize(self):
        self.load_device_list()

        self.confirm_button.clicked.connect(self.start)

    def start(self):
        try:
            self._serial_connection_manager.port = self.serial_line_input.text()
            self._serial_connection_manager.baud_rate = int(self.baud_rate_input.text())

            self._serial_connection_manager.open_serial_connection()

            self._password_resetter.remove_privileged_exec_mode_password = self.remove_privileged_exec_mode_toggle.isChecked()
            self._password_resetter.remove_line_console_password = self.remove_line_console_password_toggle.isChecked()

            self._password_resetter.set_new_privileged_exec_mode_password = self.set_new_privileged_exec_mode_password_toggle.isChecked()
            self._password_resetter.set_new_line_console_password = self.new_line_console_password_toggle.isChecked()

            if self._password_resetter.set_new_privileged_exec_mode_password:
                self._password_resetter.new_privileged_exec_mode_password = self.privileged_exec_mode_password_input.text()
            if self._password_resetter.set_new_line_console_password:
                self._password_resetter.new_line_console_password = self.line_console_password_input.text()

            self.confirm_button.enabled = False

            device = self.find_device()

            self.thread: QThread = QThread()
            self.worker = PasswordResetWorker(self._serial_connection_manager, self._password_resetter, device)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.worker.error.connect(lambda msg: logger.error(msg))

            self.confirm_button.setEnabled(False)
            self.thread.finished.connect(lambda: self.confirm_button.setEnabled(True))

            self.thread.start()

        except Exception as e:
            self._serial_connection_manager.close_connection()
            logger.error(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec_())