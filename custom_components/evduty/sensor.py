"""
EVduty charging stations terminal device and sensors
"""
from datetime import datetime

from evdutyapi import Terminal, ChargingStatus
from homeassistant.const import UnitOfPower, UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfEnergy, UnitOfTime
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from . import EVDutyCoordinator
from .const import DOMAIN, MANUFACTURER, LOGGER


async def async_setup_entry(hass, entry, async_add_devices) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for terminal in coordinator.data.values():
        LOGGER.debug(terminal)
        sensors.append(PowerSensor(coordinator, terminal))
        sensors.append(AmpSensor(coordinator, terminal))
        sensors.append(VoltSensor(coordinator, terminal))
        sensors.append(EnergyConsumedSensor(coordinator, terminal))
        sensors.append(ChargingStateSensor(coordinator, terminal))
        sensors.append(ChargingSessionStartDateSensor(coordinator, terminal))
        sensors.append(ChargingSessionDurationSensor(coordinator, terminal))
        sensors.append(ChargingSessionEstimatedCostSensor(coordinator, terminal))

    async_add_devices(sensors)


def formatted_name(name) -> str:
    return f'Charging station {name}'


def formatted_id(name) -> str:
    return slugify(name)


class EVDutyTerminalDevice(CoordinatorEntity):
    _attr_attribution = f'Data provided by {MANUFACTURER}'

    def __init__(self, coordinator: EVDutyCoordinator, terminal: Terminal) -> None:
        super().__init__(coordinator)

        self._terminal = terminal
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, terminal.id)},
            manufacturer=MANUFACTURER,
            model=terminal.charge_box_identity,
            sw_version=terminal.firmware_version,
            name=formatted_name(terminal.name))

    @callback
    def _handle_coordinator_update(self) -> None:
        self._terminal = self.coordinator.data[self._terminal.id]
        self.async_write_ha_state()


class PowerSensor(EVDutyTerminalDevice, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(self, coordinator: EVDutyCoordinator, terminal: Terminal) -> None:
        super().__init__(coordinator, terminal)
        self._attr_name = f'{formatted_name(terminal.name)} Power'
        self._attr_unique_id = f'{formatted_id(self._attr_name)}'

    @property
    def native_value(self):
        return self._terminal.session.power


class AmpSensor(EVDutyTerminalDevice, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE

    def __init__(self, coordinator: EVDutyCoordinator, terminal: Terminal) -> None:
        super().__init__(coordinator, terminal)
        self._attr_name = f'{formatted_name(terminal.name)} Amp'
        self._attr_unique_id = f'{formatted_id(self._attr_name)}'

    @property
    def native_value(self):
        return self._terminal.session.amp


class VoltSensor(EVDutyTerminalDevice, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT

    def __init__(self, coordinator: EVDutyCoordinator, terminal: Terminal) -> None:
        super().__init__(coordinator, terminal)
        self._attr_name = f'{formatted_name(terminal.name)} Volt'
        self._attr_unique_id = f'{formatted_id(self._attr_name)}'

    @property
    def native_value(self):
        return self._terminal.session.volt


class EnergyConsumedSensor(EVDutyTerminalDevice, SensorEntity):
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator: EVDutyCoordinator, terminal: Terminal) -> None:
        super().__init__(coordinator, terminal)
        self._attr_name = f'{formatted_name(terminal.name)} Energy consumed'
        self._attr_unique_id = f'{formatted_id(self._attr_name)}'

    @property
    def native_value(self):
        return self._terminal.session.energy_consumed / 1000


class ChargingStateSensor(EVDutyTerminalDevice, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ['Available', 'Charging']

    def __init__(self, coordinator: EVDutyCoordinator, terminal: Terminal) -> None:
        super().__init__(coordinator, terminal)
        self._attr_name = f'{formatted_name(terminal.name)} State'
        self._attr_unique_id = f'{formatted_id(self._attr_name)}'

    @property
    def native_value(self):
        if self._terminal.status == ChargingStatus.in_use:
            return 'Charging'
        return 'Available'


class ChargingSessionStartDateSensor(EVDutyTerminalDevice, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: EVDutyCoordinator, terminal: Terminal) -> None:
        super().__init__(coordinator, terminal)
        self._attr_name = f'{formatted_name(terminal.name)} Session Start Date'
        self._attr_unique_id = f'{formatted_id(self._attr_name)}'

    @property
    def native_value(self):
        if self._terminal.session.start_date == datetime.min:
            return None
        return self._terminal.session.start_date


class ChargingSessionDurationSensor(EVDutyTerminalDevice, SensorEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS

    def __init__(self, coordinator: EVDutyCoordinator, terminal: Terminal) -> None:
        super().__init__(coordinator, terminal)
        self._attr_name = f'{formatted_name(terminal.name)} Session Duration'
        self._attr_unique_id = f'{formatted_id(self._attr_name)}'

    @property
    def native_value(self):
        return self._terminal.session.duration.total_seconds()


class ChargingSessionEstimatedCostSensor(EVDutyTerminalDevice, SensorEntity):
    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = '$'
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator: EVDutyCoordinator, terminal: Terminal) -> None:
        super().__init__(coordinator, terminal)
        self._attr_name = f'{formatted_name(terminal.name)} Session Estimated Cost'
        self._attr_unique_id = f'{formatted_id(self._attr_name)}'

    @property
    def native_value(self):
        return self._terminal.session.cost
