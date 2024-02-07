from http import HTTPStatus
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock

from aiohttp import ClientResponseError, RequestInfo
from evdutyapi import EVDutyApi, Station, Terminal
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed

from custom_components.evduty import EVDutyCoordinator


class TestEVDutyCoordinator(IsolatedAsyncioTestCase):

    async def test_get_charging_stations(self):
        hass = Mock(HomeAssistant)
        api = Mock(EVDutyApi)
        coordinator = EVDutyCoordinator(hass=hass, api=api)

        station = Mock(Station)
        terminal = Mock(Terminal)
        terminal.id = "123"
        station.terminals = [terminal]
        api.async_get_stations = AsyncMock(return_value=[station])

        terminals = await coordinator._async_update_data()

        self.assertEqual(terminals, {"123": terminal})

    async def test_raise_on_auth_failed(self):
        hass = Mock(HomeAssistant)
        api = Mock(EVDutyApi)
        coordinator = EVDutyCoordinator(hass=hass, api=api)

        api.async_get_stations.side_effect = ClientResponseError(status=HTTPStatus.FORBIDDEN, request_info=Mock(RequestInfo), history=())

        with self.assertRaises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    async def test_raise_on_other_error(self):
        hass = Mock(HomeAssistant)
        api = Mock(EVDutyApi)
        coordinator = EVDutyCoordinator(hass=hass, api=api)

        api.async_get_stations.side_effect = ClientResponseError(status=HTTPStatus.BAD_REQUEST, request_info=Mock(RequestInfo), history=())

        with self.assertRaises(ConnectionError):
            await coordinator._async_update_data()
