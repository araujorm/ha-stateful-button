from __future__ import annotations

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, STATE_OFF, STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

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
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([StatefulCover(entry)])


class StatefulCover(CoverEntity):
    _attr_has_entity_name = False
    # GATE so the feature button uses mdi:arrow-expand-horizontal instead of
    # the up-arrow. Still inside the Security summary (door/garage/gate/window).
    _attr_device_class = CoverDeviceClass.GATE
    # supported_features is dynamic (see property below) so the Lovelace tile
    # shows exactly one button reflecting the next action:
    #   closed  -> OPEN
    #   open    -> CLOSE
    #   unknown -> OPEN (with neutral icon)

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_name = entry.data[CONF_NAME]
        self._pulse_switch: str = entry.data[CONF_PULSE_SWITCH]
        self._state_source: str | None = entry.data.get(CONF_STATE_SOURCE) or None
        self._icon_on: str = entry.data.get(CONF_ICON_ON, DEFAULT_ICON_ON)
        self._icon_off: str = entry.data.get(CONF_ICON_OFF, DEFAULT_ICON_OFF)
        self._icon_default: str = entry.data.get(CONF_ICON_DEFAULT, DEFAULT_ICON_DEFAULT)

    def _source_state(self) -> str | None:
        if not self._state_source:
            return None
        s = self.hass.states.get(self._state_source)
        if s is None or s.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        return s.state

    @property
    def is_closed(self) -> bool | None:
        s = self._source_state()
        if s == STATE_ON:
            return False
        if s == STATE_OFF:
            return True
        return None

    @property
    def state(self) -> str:
        # Override the cover's default state computation so that when there is
        # no usable source (no state_source set, or source unavailable/unknown)
        # the tile shows an empty value instead of "Unknown" / "Desconhecido".
        if self._source_state() is None:
            return ""
        return "closed" if self.is_closed else "open"

    @property
    def supported_features(self) -> CoverEntityFeature:
        s = self._source_state()
        if s == STATE_ON:   # open  -> only allow CLOSE
            return CoverEntityFeature.CLOSE
        if s == STATE_OFF:  # closed -> only allow OPEN
            return CoverEntityFeature.OPEN
        # No source defined / source unavailable: single neutral OPEN button.
        return CoverEntityFeature.OPEN

    @property
    def icon(self) -> str:
        s = self._source_state()
        if s is None:
            return self._icon_default
        if s == STATE_ON:
            return self._icon_on
        if s == STATE_OFF:
            return self._icon_off
        return self._icon_default

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        return {
            "pulse_switch": self._pulse_switch,
            "state_source": self._state_source,
        }

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        area_id = self._entry.data.get(CONF_AREA_ID)
        if area_id:
            registry = er.async_get(self.hass)
            entry = registry.async_get(self.entity_id)
            if entry and entry.area_id != area_id:
                registry.async_update_entity(self.entity_id, area_id=area_id)
        if self._state_source:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, [self._state_source], self._handle_source_change
                )
            )

    @callback
    def _handle_source_change(self, event: Event[EventStateChangedData]) -> None:
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs) -> None:
        await self._pulse()

    async def async_close_cover(self, **kwargs) -> None:
        await self._pulse()

    async def _pulse(self) -> None:
        await self.hass.services.async_call(
            "switch",
            "toggle",
            {"entity_id": self._pulse_switch},
            blocking=False,
        )
