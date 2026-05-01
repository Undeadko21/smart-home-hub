"""Switch platform for Smart Home Hub integration."""
import logging
from homeassistant.components.switch import SwitchEntity
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
    """Set up switch platform."""
    _LOGGER.info("Setting up switch platform for Smart Home Hub")
    
    # Здесь можно добавить реальные переключатели после подключения к устройству
    # Пока добавляем тестовый переключатель для демонстрации
    entities = [
        SmartHomeHubSwitch(entry.entry_id, "Test Switch")
    ]
    
    async_add_entities(entities)


class SmartHomeHubSwitch(SwitchEntity):
    """Representation of a Smart Home Hub switch."""

    def __init__(self, entry_id: str, name: str):
        """Initialize the switch."""
        self._entry_id = entry_id
        self._name = name
        self._state = False

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._entry_id}_switch_{self._name.lower().replace(' ', '_')}"

    @property
    def name(self):
        """Return the name of the switch."""
        return f"Smart Home Hub {self._name}"

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Smart Home Hub",
            "manufacturer": "Smart Home Hub",
        }

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        _LOGGER.info(f"Turning on {self._name}")
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.info(f"Turning off {self._name}")
        self._state = False
        self.async_write_ha_state()

    async def async_update(self):
        """Update the switch state."""
        # Здесь должна быть логика получения состояния от устройства
        pass
