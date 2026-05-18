from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    AreaSelector,
    EntitySelector,
    EntitySelectorConfig,
    IconSelector,
    TextSelector,
)

from .const import (
    CONF_AREA_ID,
    CONF_ICON_DEFAULT,
    CONF_ICON_OFF,
    CONF_ICON_ON,
    CONF_PULSE_SWITCH,
    CONF_STATE_SOURCE,
    DEFAULT_ICON_DEFAULT,
    DEFAULT_ICON_OFF,
    DEFAULT_ICON_ON,
    DOMAIN,
)


def _form_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): TextSelector(),
            vol.Required(
                CONF_PULSE_SWITCH, default=defaults.get(CONF_PULSE_SWITCH, vol.UNDEFINED)
            ): EntitySelector(EntitySelectorConfig(domain="switch")),
            vol.Optional(
                CONF_STATE_SOURCE, default=defaults.get(CONF_STATE_SOURCE, vol.UNDEFINED)
            ): EntitySelector(EntitySelectorConfig()),
            vol.Optional(
                CONF_AREA_ID, default=defaults.get(CONF_AREA_ID, vol.UNDEFINED)
            ): AreaSelector(),
            vol.Optional(
                CONF_ICON_ON, default=defaults.get(CONF_ICON_ON, DEFAULT_ICON_ON)
            ): IconSelector(),
            vol.Optional(
                CONF_ICON_OFF, default=defaults.get(CONF_ICON_OFF, DEFAULT_ICON_OFF)
            ): IconSelector(),
            vol.Optional(
                CONF_ICON_DEFAULT,
                default=defaults.get(CONF_ICON_DEFAULT, DEFAULT_ICON_DEFAULT),
            ): IconSelector(),
        }
    )


class StatefulButtonConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
        return self.async_show_form(step_id="user", data_schema=_form_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return StatefulButtonOptionsFlow()


class StatefulButtonOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            # Replace data wholesale instead of merging so that clearing an
            # optional field in the form actually removes it from the entry.
            self.hass.config_entries.async_update_entry(self.config_entry, data=user_input)
            return self.async_create_entry(title="", data={})
        return self.async_show_form(
            step_id="init", data_schema=_form_schema(self.config_entry.data)
        )
