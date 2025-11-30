class ConfigurationCommands:

    enable = "enable"

    exit = "exit"

    ignore_startup_config = "confreg 0x2142"

    reset_config_register_to_default = "config-register 0x2102"

    reload = "reload"

    remove_enable_secret_password = "no enable secret"

    remove_enable_password = "no enable password"

    set_enable_password = "enable password {password}"

    set_enable_secret_password = "enable secret password {password}"

    enter_line_console = "line console 0"

    set_line_console_password = "password {password}"

    enable_login = "login"

    disable_login = "no login"

    remove_line_console_password = "no password"

    end = "end"

    copy_startup_config_to_running_config = "copy startup-config running-config"

    copy_running_config_to_startup_config = "copy running-config startup-config"

    enter_global_configuration_mode = "configure terminal"

    enter_interface = "interface {interface}"

    reset_device = "reset"

    no = "no"

    yes = "yes"
