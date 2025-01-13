"""Sample API Client."""

import asyncio
import logging
import socket
from urllib.parse import urlencode

import aiohttp

TIMEOUT = 10


_LOGGER: logging.Logger = logging.getLogger(__package__)

head = {"Content-type": "application/json; charset=UTF-8"}
URL = "/api/status"


class ThermostatApiClient:
    """Representation of Thermostat Api Client."""

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        """Initialize."""
        self._session = session
        self._host = host

    async def async_get_status(self) -> dict:
        """Get the status of the device."""
        url = f"http://{self._host}{URL}"
        headers = head
        return await self.api_wrapper("get", url, headers=headers)

    async def async_set_parameter(self, value: dict) -> dict:
        """Set a parameter."""
        url = f"http://{self._host}{URL}"
        headers = head
        return await self.api_wrapper(
            "post",
            url,
            data=value,
            headers=headers,
        )

    async def async_play(self) -> None:
        url = f"http://{self._host}/api/pandora/play"
        headers = head
        return await self.api_wrapper("get", url, headers=headers)

    async def async_pause(self) -> None:
        url = f"http://{self._host}/api/pandora/pause"
        headers = head
        return await self.api_wrapper("get", url, headers=headers)

    async def async_on(self) -> None:
        url = f"http://{self._host}/api/pandora/on"
        headers = head
        return await self.api_wrapper("get", url, headers=headers)

    async def async_off(self) -> None:
        url = f"http://{self._host}/api/pandora/off"
        headers = head
        return await self.api_wrapper("get", url, headers=headers)

    async def async_next(self) -> None:
        url = f"http://{self._host}/api/pandora/next"
        headers = head
        return await self.api_wrapper("get", url, headers=headers)

    async def async_changestation(self, stationName: str) -> None:
        myqs = {"stationName": stationName}
        url = f"http://{self._host}/api/pandora/changestation?{urlencode(myqs)}"
        headers = head
        return await self.api_wrapper("get", url, headers=headers)

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            async with asyncio.timeout(TIMEOUT):
                if method == "get":
                    response = await self._session.get(url, headers=headers, ssl=False)
                    _LOGGER.info(await response.json())
                    return await response.json()

                if method == "put":
                    await self._session.put(url, headers=headers, json=data, ssl=False)

                elif method == "patch":
                    await self._session.patch(
                        url, headers=headers, json=data, ssl=False
                    )

                elif method == "post":
                    response = await self._session.post(
                        url, headers=headers, json=data, ssl=False
                    )
                    return await response.json()

        except TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
        return {}
