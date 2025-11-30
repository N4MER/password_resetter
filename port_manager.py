import serial.tools.list_ports

class PortManager:

    @staticmethod
    def list_ports() -> list:
        ports = serial.tools.list_ports.comports()
        return ports

    @staticmethod
    def load_ports(port_list: list):
        for port in PortManager.list_ports():
            port_list.append(port.device)