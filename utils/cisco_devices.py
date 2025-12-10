from dataclasses import dataclass

class BootEnvironment:
    ROMMON = "ROMMON"
    SWITCH_BOOTLOADER = "SWITCH_BOOTLOADER"

@dataclass(frozen=True)
class Device:
    model: str
    device: str
    boot_environment: str


class Devices:
    devices = [
        Device("ISR 4321", "Router", BootEnvironment.ROMMON),
        Device("ISR 4331", "Router", BootEnvironment.ROMMON),
        Device("ISR 4351", "Router", BootEnvironment.ROMMON),
        Device("ASR 1001-X", "Router", BootEnvironment.ROMMON),
        Device("ASR 1002-X", "Router", BootEnvironment.ROMMON),

        Device("Catalyst 2950", "Switch", BootEnvironment.SWITCH_BOOTLOADER),
        Device("Catalyst 2960", "Switch", BootEnvironment.SWITCH_BOOTLOADER),
        Device("Catalyst 2960X", "Switch", BootEnvironment.SWITCH_BOOTLOADER),
        Device("Catalyst 3560", "Switch", BootEnvironment.SWITCH_BOOTLOADER),
        Device("Catalyst 3750", "Switch", BootEnvironment.SWITCH_BOOTLOADER)
    ]

