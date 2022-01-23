"""The HTTP Thermostat integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ThermostatApiClient
from .const import CONF_HOST, DOMAIN, PLATFORMS, STARTUP_MESSAGE

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    host = str(entry.data.get(CONF_HOST))

    session = async_get_clientsession(hass)
    client = ThermostatApiClient(host=host, session=session)

    coordinator = ThermostatUpdateCoordinator(hass, client=client)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # for platform in PLATFORMS:
    #     if entry.options.get(platform, True):
    #         coordinator.platforms.append(platform)
    #         hass.async_add_job(
    #             hass.config_entries.async_forward_entry_setup(entry, platform)
    #         )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    entry.add_update_listener(async_reload_entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
    #    hass.data[DOMAIN].pop(entry.entry_id)

    # return unload_ok

    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


SCAN_INTERVAL = timedelta(seconds=30)


class ThermostatUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: ThermostatApiClient,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms: list[str] = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Get Status."""
        try:
            status = await self.api.async_get_status()
            response = status
            return response
        except Exception as exception:
            raise UpdateFailed() from exception
