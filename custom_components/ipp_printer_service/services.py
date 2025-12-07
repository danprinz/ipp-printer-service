import logging
import os
from datetime import datetime

import aiofiles
from pyipp import IPP
from pyipp.enums import IppOperation
from pyipp.exceptions import IPPError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
    CONF_VERIFY_SSL,
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_SIMULATION_MODE

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant):
    """Set up the IPP Printer Service services."""

    async def async_print_pdf(call: ServiceCall):
        """Handle the print_pdf service call."""
        entity_id = call.data.get("entity_id")
        file_path_template = call.data.get("file_path")

        if not isinstance(file_path_template, str):
            raise HomeAssistantError("File path must be a string template")

        from homeassistant.helpers import template

        tpl = template.Template(file_path_template, hass)
        file_path = tpl.async_render(parse_result=False)

        if not entity_id:
            raise HomeAssistantError("Entity ID is required")
        if not file_path:
            raise HomeAssistantError("File path is required")

        if not os.path.exists(file_path):
            raise HomeAssistantError(f"File not found: {file_path}")

        registry = er.async_get(hass)
        entry = registry.async_get(entity_id)

        if not entry:
            raise HomeAssistantError(f"Entity not found: {entity_id}")

        if not entry.config_entry_id:
            raise HomeAssistantError(
                f"Entity {entity_id} is not linked to a config entry"
            )

        config_entry = hass.config_entries.async_get_entry(entry.config_entry_id)

        if not config_entry:
            raise HomeAssistantError(f"Config entry not found for {entity_id}")

        if config_entry.domain != "ipp_printer_service":
            raise HomeAssistantError(
                f"Entity {entity_id} is not an IPP Printer Service entity"
            )

        # Check for simulation mode
        if config_entry.options.get(CONF_SIMULATION_MODE, False):
            _LOGGER.info(f"Simulation mode active. Printing {file_path} simulated.")
            coordinator = config_entry.runtime_data
            coordinator.async_set_last_job(
                {
                    "entity_id": entity_id,
                    "file_path": file_path,
                    "timestamp": str(datetime.now()),
                    "status": "simulated",
                }
            )
            # Cleanup
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                _LOGGER.warning(f"Failed to remove temporary file {file_path}: {e}")
            return

        # Create a fresh IPP client using config entry data
        host = config_entry.data.get(CONF_HOST)
        port = config_entry.data.get(CONF_PORT)
        base_path = config_entry.data.get("base_path")
        ssl = config_entry.data.get(CONF_SSL, False)
        verify_ssl = config_entry.data.get(CONF_VERIFY_SSL, True)
        username = config_entry.data.get("username")
        password = config_entry.data.get("password")

        session = async_get_clientsession(hass)

        ipp = IPP(
            host=host,
            port=port,
            base_path=base_path,
            tls=ssl,
            verify_ssl=verify_ssl,
            session=session,
            username=username,
            password=password,
        )

        try:
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()

            _LOGGER.info(
                f"Printing {file_path} to {host}:{port}{base_path} (SSL={ssl})"
            )

            message = {
                "operation-attributes-tag": {
                    "requesting-user-name": "Home Assistant",
                    "job-name": "Attendance Doc",
                    "document-format": "application/pdf",
                },
                "data": content,
            }

            await ipp.execute(IppOperation.PRINT_JOB, message)
            _LOGGER.info(f"Successfully printed {file_path} to {entity_id}")

            # Update last job for real prints too
            coordinator = config_entry.runtime_data
            coordinator.async_set_last_job(
                {
                    "entity_id": entity_id,
                    "file_path": file_path,
                    "timestamp": str(datetime.now()),
                    "status": "success",
                }
            )

        except Exception as e:
            _LOGGER.error(f"Failed to print {file_path}: {e}")
            raise HomeAssistantError(f"Failed to print: {e}")
        finally:
            # Cleanup the file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                _LOGGER.warning(f"Failed to remove temporary file {file_path}: {e}")

    hass.services.async_register("ipp_printer_service", "print_pdf", async_print_pdf)
