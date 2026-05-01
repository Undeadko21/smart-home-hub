"""Config flow for Smart Home Hub integration."""
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from . import DOMAIN
from .const import CONF_HOST, CONF_PORT, DEFAULT_PORT


class SmartHomeHubConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Home Hub."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Smart Home Hub", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> "OptionsFlow":
        """Get the options flow for this handler."""
        return OptionsFlow()


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(step_id="user")
