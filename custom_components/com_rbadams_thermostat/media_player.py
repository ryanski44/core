"""Platform for light integration."""

from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ThermostatUpdateCoordinator
from .const import DEFAULT_NAME, DOMAIN, MEDIA_PLAYER

# Import the device class from the component that you want to support
# import homeassistant.helpers.config_validation as cv


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
):
    """Set up the entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([PandoraMediaPlayer(coordinator)])


class PandoraMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """Representation of a Pandora Media Player."""

    def __init__(self, coordinator: ThermostatUpdateCoordinator):
        """Init."""
        super().__init__(coordinator)
        self.api = coordinator.api

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the current state of the media player."""
        if not self.coordinator.data or not self.coordinator.data["pandora"]:
            return MediaPlayerState.OFF
        state = self.coordinator.data["pandora"]["state"]
        return {
            "OFF": MediaPlayerState.OFF,
            "ON": MediaPlayerState.ON,
            "PLAYING": MediaPlayerState.PLAYING,
            "PAUSED": MediaPlayerState.PAUSED,
        }.get(state, MediaPlayerState.OFF)

    @property
    def supported_features(self):
        """Flag media player features that are supported"""
        return (
            MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.SELECT_SOURCE
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.TURN_ON
        )

    @property
    def media_content_type(self) -> MediaType | None:
        """Return the content type of currently playing media."""
        return MediaType.CHANNEL

    @property
    def media_title(self) -> str | None:
        """Title of current playing media."""
        return self.coordinator.data["pandora"]["currentSong"]

    @property
    def media_artist(self) -> str | None:
        """Artist of current playing media, music track only."""
        return self.coordinator.data["pandora"]["currentArtist"]

    @property
    def media_album_name(self) -> str | None:
        """Album of current playing media, music track only."""
        return self.coordinator.data["pandora"]["currentAlbum"]

    @property
    def source_list(self):
        """List of available input sources."""
        return self.coordinator.data["pandora"]["stationList"]

    async def async_media_play(self) -> None:
        """Send play command."""
        await self.api.async_play()
        await self.coordinator.async_request_refresh()

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self.api.async_pause()
        await self.coordinator.async_request_refresh()

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self.api.async_next()
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self):
        """Turn the media player on."""
        await self.api.async_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        """Turn the media player off."""
        await self.api.async_off()
        await self.coordinator.async_request_refresh()

    async def async_select_source(self, source):
        """Select input source."""
        await self.api.async_changestation(source)
        await self.coordinator.async_request_refresh()

    @property
    def name(self) -> str:
        """Return the name of the device, if any."""
        return f"{DEFAULT_NAME}_{MEDIA_PLAYER}"
