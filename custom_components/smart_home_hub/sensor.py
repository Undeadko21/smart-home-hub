"""Sensor platform for Smart Home Hub integration."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    _LOGGER.info("Setting up sensor platform for Smart Home Hub")
    
    # Здесь можно добавить реальные сенсоры после подключения к устройству
    # Пока добавляем тестовый сенсор для демонстрации
    entities = [
        SmartHomeHubSensor(entry.entry_id, "Test Sensor", "temperature", "°C")
    ]
    
    async_add_entities(entities)


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
        # Здесь должна быть логика получения данных от устройства
        self._state = 22.5  # Тестовое значение
