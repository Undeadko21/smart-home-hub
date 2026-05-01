"""Config flow for Smart Home Hub integration."""
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol
import httpx

from . import DOMAIN
from .const import CONF_HOST, CONF_PORT, DEFAULT_PORT, CONF_API_KEY


class SmartHomeHubConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Home Hub."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate connection
            host = user_input.get(CONF_HOST, "")
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            api_key = user_input.get(CONF_API_KEY, "")
            
            base_url = f"{host.rstrip('/')}:{port}"
            
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    headers = {}
                    if api_key:
                        headers["Authorization"] = f"Bearer {api_key}"
                    
                    response = await client.get(f"{base_url}/api/health", headers=headers)
                    if response.status_code == 200:
                        return self.async_create_entry(title="Smart Home Hub", data=user_input)
                    else:
                        errors["base"] = "cannot_connect"
            except httpx.HTTPError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            
            # Only create entry if no errors
            if not errors:
                return self.async_create_entry(title="Smart Home Hub", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="http://localhost"): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_API_KEY, default=""): str,
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
        
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=self.config_entry.data.get(CONF_HOST, "")): str,
                vol.Optional(CONF_PORT, default=self.config_entry.data.get(CONF_PORT, DEFAULT_PORT)): int,
                vol.Optional(CONF_API_KEY, default=self.config_entry.data.get(CONF_API_KEY, "")): str,
            }
        )
        
        return self.async_show_form(step_id="user", data_schema=data_schema)
