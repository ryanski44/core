"""Platform for light integration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PRECISION_TENTHS, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ThermostatUpdateCoordinator
from .const import CLIMATE, DEFAULT_NAME, DOMAIN

# Import the device class from the component that you want to support
# import homeassistant.helpers.config_validation as cv


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_devices: Callable[[list[ClimateEntity]], None],
):
    """Set up the entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([HTTPThermostat(coordinator)])


# {
#   "sensors":[{"name":"upstairs","temperature":72.49999999999999,"relativeHumidity":0.276}],
#   "temperatureAverage": 72.94999999999999,
#   "relativeHumidityAverage": 0.3990000000000001,
#   "heat": false,
#   "cool": false,
#   "fan": false,
#   "scheduleEnabled": true,
#   "minTemp": 73,
#   "maxTemp": 79,
#   "maxTempDifferential": 3
# }


class HTTPThermostat(CoordinatorEntity, ClimateEntity):
    """Representation of a Thermostat."""

    def __init__(self, coordinator: ThermostatUpdateCoordinator):
        """Init."""
        super().__init__(coordinator)
        self.api = coordinator.api

    @property
    def current_humidity(self) -> int:
        """Return humidity."""
        return int(self.coordinator.data["relativeHumidityAverage"] * 100)

    @property
    def temperature_unit(self):
        """Return temperature unit."""
        return UnitOfTemperature.FAHRENHEIT

    @property
    def target_temperature_step(self) -> float:
        """Return target temperature step."""
        return PRECISION_WHOLE

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return hvac modes."""
        return [HVACMode.AUTO]

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return supported features."""
        return ClimateEntityFeature.TARGET_TEMPERATURE_RANGE

    @property
    def name(self) -> str:
        """Return the name of the device, if any."""
        return f"{DEFAULT_NAME}_{CLIMATE}"

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode."""
        return HVACMode.AUTO

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return hvac action."""
        data = self.coordinator.data
        if str(data["heat"]).lower() == "true":
            return HVACAction.HEATING
        if str(data["cool"]).lower() == "true":
            return HVACAction.COOLING
        if str(data["fan"]).lower() == "true":
            return HVACAction.FAN
        return HVACAction.OFF

    @property
    def icon(self) -> str:
        """Return nice icon for heater."""
        if self.hvac_action == HVACAction.HEATING:
            return "mdi:fire"
        if self.hvac_action == HVACAction.COOLING:
            return "mdi:air-conditioner"
        if self.hvac_action == HVACAction.FAN:
            return "mdi:fan"
        return "mdi:radiator-off"

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set hvac mode."""
        return

    @property
    def precision(self) -> float:
        """Return the precision of the temperature"""
        return PRECISION_TENTHS

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return float(self.coordinator.data["temperatureAverage"])

    @property
    def target_temperature_high(self) -> float | None:
        """Return the temperature we try to be lower than."""
        return float(self.coordinator.data["maxTemp"])

    @property
    def target_temperature_low(self) -> float | None:
        """Return the temperature we try to be higher than."""
        return float(self.coordinator.data["minTemp"])

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        min = kwargs.get(ATTR_TARGET_TEMP_LOW)
        max = kwargs.get(ATTR_TARGET_TEMP_HIGH)
        if min is None and max is None:
            return
        data = self.coordinator.data
        data["minTemp"] = min
        data["maxTemp"] = max
        await self.api.async_set_parameter(data)
        await self.coordinator.async_request_refresh()
