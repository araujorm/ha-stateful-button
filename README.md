# Stateful Button

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration that fuses a momentary pulse switch
and a separate contact sensor into a single tile with visible state and
a single-press action.

Useful for garage door openers, gates, intercom door buzzers and similar
devices where the actuator is a momentary switch and the open/closed
state is reported by a different entity.

## What you get

For each configured instance the integration creates a `cover.*` entity
that:

- shows up in the auto-overview's Security summary (device class `gate`,
  but the entity icon is configurable to anything you like)
- displays a single command button on the tile (no open/close arrow
  pair) that, when pressed, toggles the configured pulse switch
- mirrors its state from a separate "state source" entity (typically a
  contact `binary_sensor`); the tile shows blank until a state source is
  configured

## Install via HACS

1. HACS -> three-dot menu -> *Custom repositories*
2. Add this repo URL with category **Integration**
3. Install *Stateful Button*
4. Restart Home Assistant
5. *Settings -> Devices & Services -> Add Integration -> Stateful Button*

## Manual install

Copy `custom_components/stateful_button/` to your HA `config/custom_components/`
directory and restart Home Assistant.

## Configuration

Everything is set up through the UI config flow. Fields:

| Field            | Required | Notes                                                                  |
|------------------|----------|------------------------------------------------------------------------|
| Name             | yes      | Display name of the entity.                                            |
| Pulse switch     | yes      | The `switch.*` entity that is toggled on each press.                   |
| State source     | no       | An entity (typically a contact `binary_sensor`) whose state drives the cover's open/closed state. Leave empty for a stateless press. |
| Area             | no       | Area to assign the entity to.                                          |
| Icon when on     | no       | mdi icon shown when the source state is `on` (default `mdi:garage-open`). |
| Icon when off    | no       | mdi icon shown when the source state is `off` (default `mdi:garage`).  |
| Icon when unknown| no       | mdi icon used when the source state is unavailable or unknown (default `mdi:garage-alert`). |

All options are editable later via *Configure* on the integration's entry.

## License

MIT - see [LICENSE](LICENSE).
