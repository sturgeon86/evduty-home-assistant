import asyncio
from datetime import timedelta
from http import HTTPStatus

from aiohttp import ClientResponseError
from evdutyapi import EVDutyApi, Terminal
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class EVDutyCoordinator(DataUpdateCoordinator):
    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, api: EVDutyApi) -> None:
        super().__init__(hass=hass, logger=LOGGER, name=DOMAIN, update_interval=timedelta(seconds=30))
        self.api = api

    async def _async_update_data(self) -> dict[str, Terminal]:
        try:
            async with asyncio.timeout(10):
                stations = await self.api.async_get_stations()
                return {terminal.id: terminal for station in stations for terminal in station.terminals}
        except ClientResponseError as error:
            if error.status == HTTPStatus.FORBIDDEN:
                raise ConfigEntryAuthFailed from error
            raise ConnectionError from error
