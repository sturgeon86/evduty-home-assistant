"""
EVduty charging stations config flow
"""
from __future__ import annotations

from http import HTTPStatus
from typing import Any

import voluptuous as vol
from aiohttp import ClientResponseError
from evdutyapi import EVDutyApi
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import DOMAIN, LOGGER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class EVDutyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, data: dict[str, Any] | None = None) -> FlowResult:

        if data is None:
            return self.async_show_form(step_id='user', data_schema=STEP_USER_DATA_SCHEMA)

        errors: dict[str, str] = {}
        try:
            evduty_api = EVDutyApi(data[CONF_USERNAME], data[CONF_PASSWORD], async_create_clientsession(self.hass))
            await evduty_api.async_authenticate()
            return self.async_create_entry(title=data[CONF_USERNAME], data=data)
        except ClientResponseError as error:
            LOGGER.error(error)
            if error.status == HTTPStatus.BAD_REQUEST:
                errors['base'] = 'invalid_auth'
            else:
                errors['base'] = 'cannot_connect'
        except Exception:
            LOGGER.exception('Unexpected exception')
            errors['base'] = 'unknown'

        return self.async_show_form(step_id='user', data_schema=STEP_USER_DATA_SCHEMA, errors=errors)
