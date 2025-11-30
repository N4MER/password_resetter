import re
from re import Pattern

class ResponsePatterns:
    ROMMON: Pattern[str] = re.compile(r'rommon|rommon.*\d+>|rommon.*>', re.IGNORECASE | re.MULTILINE)

    EXEC_MODE: Pattern[str] = re.compile(r'^[^\n\r]*>$', re.MULTILINE)

    PRIVILEGED_EXEC_MODE: Pattern[str] = re.compile(r'^[^\n\r]*#$', re.MULTILINE)

    GLOBAL_CONFIG: Pattern[str] = re.compile(r'^\(config\)#$', re.MULTILINE)

    INITIAL_SETUP_MESSAGE: Pattern[str] = re.compile(r'^(Would you like to enter the initial configuration dialog\?)',re.MULTILINE | re.IGNORECASE)

    #interface config mode