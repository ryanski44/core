"""Constants for the HTTP Thermostat integration."""

NAME = "HTTP Thermostat (rbadams.com)"
VERSION = "0.0.1"

DOMAIN = "com_rbadams_thermostat"
DOMAIN_DATA = f"{DOMAIN}_data"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration for a respberry pi based custom thermostat!
-------------------------------------------------------------------
"""

# Platforms
CLIMATE = "climate"
PLATFORMS = [CLIMATE]

# Defaults
DEFAULT_NAME = DOMAIN

# Configuration and options
CONF_HOST = "host"
