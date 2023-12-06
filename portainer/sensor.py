"""Platform for sensor integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from ssl import PROTOCOL_TLS_CLIENT, SSLContext
from typing import Any, Optional

from aiohttp import ClientSession

from homeassistant import core
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .port import PortainerContainerStatus

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=6)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: ConfigEntries.ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the sensor platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    session = async_get_clientsession(hass)
    certificate = config["ca_cert_pem"]
    context = SSLContext(PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cadata=certificate)
    async_add_entities(
        [PortainerSensor(config, session, context)], update_before_add=True
    )


class PortainerSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "portainer"
    _attr_native_unit_of_measurement = "pending update(s)"

    def __init__(
        self, config: dict[str, str], session: ClientSession, context: SSLContext
    ) -> None:
        """init."""
        super().__init__()
        self.user = config[CONF_USERNAME]
        self.password = config[CONF_PASSWORD]
        self.hostname = config[CONF_HOST]
        self.port = config[CONF_PORT]
        self.context = context
        self.session = session
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self.hostname

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.hostname

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        """state."""
        return self._state

    @property
    def device_state_attributes(self) -> dict[str, Any]:
        """State attributes."""
        return self.attrs

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        host = f"https://{self.hostname}:{self.port}"
        p = PortainerContainerStatus(
            self.session, self.context, host, self.user, self.password
        )
        await p.get_auth_token()
        cont = await p.get_containers()
        updates = [u for u in cont if u.update_available]
        self._state = len(updates)
        self._attr_native_value = len(updates)
        self._attr_extra_state_attributes = {
            "containers": [
                {"name": c.name, "status": c.status, "state": c.state} for c in updates
            ]
        }
