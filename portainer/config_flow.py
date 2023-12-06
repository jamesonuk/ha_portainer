"""Config flow for Portainer Check."""
from __future__ import annotations

import logging
import os
from pathlib import Path
import tempfile
from typing import Any, Optional

import voluptuous as vol

from homeassistant.components.file_upload import process_uploaded_file
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    FileSelector,
    FileSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from homeassistant.helpers.typing import ConfigType

from .const import CONF_CA_CERTIFICATE, DOMAIN

TEMP_DIR_NAME = f"home-assistant-{DOMAIN}"

_LOGGER = logging.getLogger(__name__)

PORTAINER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Required(CONF_CA_CERTIFICATE): FileSelector(
            FileSelectorConfig(accept=".crt,application/x-x509-ca-cert")
        ),
    }
)


async def async_create_certificate_temp_files(
    hass: HomeAssistant, config: ConfigType
) -> None:
    """Create certificate temporary files for the Portainer Check."""

    def _create_temp_file(temp_file: Path, data: str | None) -> None:
        if data is None or data == "auto":
            if temp_file.exists():
                os.remove(Path(temp_file))
            return
        temp_file.write_text(data)

    def _create_temp_dir_and_files() -> None:
        """Create temporary directory."""
        temp_dir = Path(tempfile.gettempdir()) / TEMP_DIR_NAME

        if config.get(CONF_CA_CERTIFICATE) and not temp_dir.exists():
            temp_dir.mkdir(0o700)

        _create_temp_file(
            temp_dir / CONF_CA_CERTIFICATE, config.get(CONF_CA_CERTIFICATE)
        )

    await hass.async_add_executor_job(_create_temp_dir_and_files)


class FlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None):
        """When a user initiates a flow via the user interface."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # Validate parameters here
            certificate_id: str | None = user_input[CONF_CA_CERTIFICATE]
            if certificate_id:
                with process_uploaded_file(
                    self.hass, certificate_id
                ) as certificate_file:
                    user_input["ca_cert_pem"] = certificate_file.read_text(
                        encoding="utf-8"
                    )
            if not errors:
                return self.async_create_entry(title="Portainer Check", data=user_input)
        return self.async_show_form(
            step_id="user", data_schema=PORTAINER_SCHEMA, errors=errors
        )
