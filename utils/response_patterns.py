import re

class ResponsePatterns:
    ROMMON = re.compile(r'rommon|rommon.*\d+>|rommon.*>', re.IGNORECASE | re.MULTILINE)

    BOOTLOADER = re.compile(r'^switch:\s*$', re.IGNORECASE | re.MULTILINE)

    EXEC_MODE = re.compile(r'^[^\n\r]*>$', re.MULTILINE)

    PRIVILEGED_EXEC_MODE = re.compile(r'^[^\n\r]*#$', re.MULTILINE)

    GLOBAL_CONFIGURATION_MODE = re.compile(r'^\(config\)#$', re.MULTILINE)

    INITIAL_SETUP_MESSAGE = re.compile(r'^(Would you like to enter the initial configuration dialog\?)', re.MULTILINE | re.IGNORECASE)

    LINE_CONFIGURATION_MODE = re.compile(r'^\([^\n\r]*-line\)#$', re.MULTILINE)

    INTERFACE_CONFIGURATION_MODE = re.compile(r'^\([^\n\r]*-if\)#$', re.MULTILINE)

    ROUTER_CONFIGURATION_MODE = re.compile(r'^\([^\n\r]*-router\)#$', re.MULTILINE)

    SUB_INTERFACE_CONFIGURATION_MODE = re.compile(r'^\([^\n\r]*-subif\)#$', re.MULTILINE)

    DESTINATION_FILE_RENAME = re.compile(r'Destination\s+filename\s*\[[^\]]*\]\s*\?', re.MULTILINE | re.IGNORECASE)

    PROCEED_WITH_RELOAD = re.compile(r'Proceed\s+with\s+reload\??', re.IGNORECASE | re.MULTILINE)
