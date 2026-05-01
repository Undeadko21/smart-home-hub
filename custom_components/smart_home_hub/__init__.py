"""Smart Home Hub integration for Home Assistant."""
import logging
import httpx
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "switch"]


class SmartHomeHubCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Smart Home Hub."""

    def __init__(self, hass: HomeAssistant, host: str, port: int, api_key: str = ""):
        """Initialize the coordinator."""
        self.host = host
        self.port = port
        self.api_key = api_key
        self.base_url = f"{host.rstrip('/')}:{port}"
        self.client = httpx.AsyncClient(timeout=10)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=30,  # Update every 30 seconds
        )

    async def _async_update_data(self):
        """Fetch data from the Smart Home Hub API."""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Fetch devices/entities from the hub
            response = await self.client.get(f"{self.base_url}/api/ha/entities", headers=headers)
            response.raise_for_status()
            entities = response.json()
            return {"entities": entities, "status": "connected", "entity_count": len(entities)}
        except httpx.HTTPError as err:
            _LOGGER.warning(f"Error fetching data from Smart Home Hub: {err}")
            return {"entities": [], "status": "error", "error": str(err)}
        except Exception as err:
            _LOGGER.error(f"Unexpected error: {err}")
            return {"entities": [], "status": "error", "error": str(err)}

    async def async_call_service(self, domain: str, service: str, data: dict = None, target: dict = None):
        """Call a service on the Smart Home Hub."""
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            payload = {
                "domain": domain,
                "service": service,
                "data": data or {},
                "target": target or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/ha/call_service",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            # Refresh data after calling a service
            await self.async_request_refresh()
            
            return result
        except httpx.HTTPError as err:
            _LOGGER.error(f"Error calling service {domain}.{service}: {err}")
            raise


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Smart Home Hub component from yaml configuration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Home Hub from a config entry."""
    _LOGGER.info("Setting up Smart Home Hub integration")
    
    host = entry.data.get(CONF_HOST)
    port = entry.data.get(CONF_PORT, 8080)
    api_key = entry.data.get(CONF_API_KEY, "")
    
    _LOGGER.info(f"Connecting to Smart Home Hub at {host}:{port}")
    
    # Create coordinator
    coordinator = SmartHomeHubCoordinator(hass, host, port, api_key)
    
    # Perform initial fetch
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "host": host,
        "port": port,
        "api_key": api_key,
        "coordinator": coordinator,
    }
    
    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Close the HTTP client
        coordinator = hass.data[DOMAIN][entry.entry_id].get("coordinator")
        if coordinator:
            await coordinator.client.aclose()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
