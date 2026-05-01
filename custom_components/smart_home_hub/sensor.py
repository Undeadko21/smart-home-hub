"""Sensor platform for Smart Home Hub integration."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    _LOGGER.info("Setting up sensor platform for Smart Home Hub")
    
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    # Create sensors based on coordinator data
    entities = []
    
    # Add a status sensor
    entities.append(SmartHomeHubStatusSensor(coordinator, entry.entry_id))
    
    async_add_entities(entities)


class SmartHomeHubStatusSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Smart Home Hub status sensor."""

    def __init__(self, coordinator, entry_id: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._name = "Connection Status"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._entry_id}_status"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Smart Home Hub {self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("status", "unknown")
        return "unknown"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        attrs = {}
        if self.coordinator.data:
            attrs["status"] = self.coordinator.data.get("status", "unknown")
            attrs["error"] = self.coordinator.data.get("error")
            attrs["entity_count"] = len(self.coordinator.data.get("entities", []))
            attrs["host"] = self.coordinator.host
            attrs["port"] = self.coordinator.port
        return attrs

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Smart Home Hub",
            "manufacturer": "Smart Home Hub",
        }


class SmartHomeHubSensor(SensorEntity):
    """Representation of a Smart Home Hub sensor."""

    def __init__(self, entry_id: str, name: str, sensor_type: str, unit: str):
        """Initialize the sensor."""
        self._entry_id = entry_id
        self._name = name
        self._sensor_type = sensor_type
        self._unit = unit
        self._state = None

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._entry_id}_{self._sensor_type}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Smart Home Hub {self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Smart Home Hub",
            "manufacturer": "Smart Home Hub",
        }

    async def async_update(self):
        """Update the sensor state."""
        # Here should be logic to get data from the device
        self._state = 22.5  # Test value
