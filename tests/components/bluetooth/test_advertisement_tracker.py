"""Tests for the Bluetooth integration advertisement tracking."""

from datetime import timedelta
import time
from unittest.mock import patch

from bleak.backends.scanner import AdvertisementData, BLEDevice

from homeassistant.components.bluetooth import (
    BaseHaScanner,
    async_register_scanner,
    async_track_unavailable,
)
from homeassistant.components.bluetooth.advertisement_tracker import (
    ADVERTISING_TIMES_NEEDED,
)
from homeassistant.components.bluetooth.const import (
    SOURCE_LOCAL,
    UNAVAILABLE_TRACK_SECONDS,
)
from homeassistant.core import callback
from homeassistant.util import dt as dt_util

from . import (
    generate_advertisement_data,
    inject_advertisement_with_time_and_source,
    inject_advertisement_with_time_and_source_connectable,
)

from tests.common import async_fire_time_changed

ONE_HOUR_SECONDS = 3600


async def test_advertisment_interval_shorter_than_adapter_stack_timeout(
    hass, caplog, enable_bluetooth, macos_adapter
):
    """Test we can determine the advertisement interval."""
    start_monotonic_time = time.monotonic()
    switchbot_device = BLEDevice("44:44:33:11:23:12", "wohand")
    switchbot_adv = generate_advertisement_data(
        local_name="wohand", service_uuids=["cba20d00-224d-11e6-9fb8-0002a5d5c51b"]
    )
    switchbot_device_went_unavailable = False

    @callback
    def _switchbot_device_unavailable_callback(_address: str) -> None:
        """Switchbot device unavailable callback."""
        nonlocal switchbot_device_went_unavailable
        switchbot_device_went_unavailable = True

    for i in range(ADVERTISING_TIMES_NEEDED):
        inject_advertisement_with_time_and_source(
            hass,
            switchbot_device,
            switchbot_adv,
            start_monotonic_time + (i * 2),
            SOURCE_LOCAL,
        )

    switchbot_device_unavailable_cancel = async_track_unavailable(
        hass, _switchbot_device_unavailable_callback, switchbot_device.address
    )

    monotonic_now = start_monotonic_time + ((ADVERTISING_TIMES_NEEDED - 1) * 2)
    with patch(
        "homeassistant.components.bluetooth.manager.MONOTONIC_TIME",
        return_value=monotonic_now + UNAVAILABLE_TRACK_SECONDS,
    ):
        async_fire_time_changed(
            hass, dt_util.utcnow() + timedelta(seconds=UNAVAILABLE_TRACK_SECONDS)
        )
        await hass.async_block_till_done()

    assert switchbot_device_went_unavailable is True
    switchbot_device_unavailable_cancel()


async def test_advertisment_interval_longer_than_adapter_stack_timeout_connectable(
    hass, caplog, enable_bluetooth, macos_adapter
):
    """Test device with a long advertisement interval."""
    start_monotonic_time = time.monotonic()
    switchbot_device = BLEDevice("44:44:33:11:23:18", "wohand")
    switchbot_adv = generate_advertisement_data(
        local_name="wohand", service_uuids=["cba20d00-224d-11e6-9fb8-0002a5d5c51b"]
    )
    switchbot_device_went_unavailable = False

    @callback
    def _switchbot_device_unavailable_callback(_address: str) -> None:
        """Switchbot device unavailable callback."""
        nonlocal switchbot_device_went_unavailable
        switchbot_device_went_unavailable = True

    for i in range(ADVERTISING_TIMES_NEEDED):
        inject_advertisement_with_time_and_source(
            hass,
            switchbot_device,
            switchbot_adv,
            start_monotonic_time + (i * ONE_HOUR_SECONDS),
            SOURCE_LOCAL,
        )

    switchbot_device_unavailable_cancel = async_track_unavailable(
        hass, _switchbot_device_unavailable_callback, switchbot_device.address
    )

    monotonic_now = start_monotonic_time + (
        (ADVERTISING_TIMES_NEEDED - 1) * ONE_HOUR_SECONDS
    )
    with patch(
        "homeassistant.components.bluetooth.manager.MONOTONIC_TIME",
        return_value=monotonic_now + UNAVAILABLE_TRACK_SECONDS,
    ):
        async_fire_time_changed(
            hass, dt_util.utcnow() + timedelta(seconds=UNAVAILABLE_TRACK_SECONDS)
        )
        await hass.async_block_till_done()

    assert switchbot_device_went_unavailable is True
    switchbot_device_unavailable_cancel()


async def test_advertisment_interval_longer_than_adapter_stack_timeout_adapter_change_connectable(
    hass, caplog, enable_bluetooth, macos_adapter
):
    """Test device with a long advertisement interval with an adapter change."""
    start_monotonic_time = time.monotonic()
    switchbot_device = BLEDevice("44:44:33:11:23:45", "wohand")
    switchbot_adv = generate_advertisement_data(
        local_name="wohand", service_uuids=["cba20d00-224d-11e6-9fb8-0002a5d5c51b"]
    )
    switchbot_device_went_unavailable = False

    @callback
    def _switchbot_device_unavailable_callback(_address: str) -> None:
        """Switchbot device unavailable callback."""
        nonlocal switchbot_device_went_unavailable
        switchbot_device_went_unavailable = True

    for i in range(ADVERTISING_TIMES_NEEDED):
        inject_advertisement_with_time_and_source(
            hass,
            switchbot_device,
            switchbot_adv,
            start_monotonic_time + (i * 2),
            "original",
        )

    for i in range(ADVERTISING_TIMES_NEEDED):
        inject_advertisement_with_time_and_source(
            hass,
            switchbot_device,
            switchbot_adv,
            start_monotonic_time + (i * ONE_HOUR_SECONDS),
            "new",
        )

    switchbot_device_unavailable_cancel = async_track_unavailable(
        hass, _switchbot_device_unavailable_callback, switchbot_device.address
    )

    monotonic_now = start_monotonic_time + (
        (ADVERTISING_TIMES_NEEDED - 1) * ONE_HOUR_SECONDS
    )
    with patch(
        "homeassistant.components.bluetooth.manager.MONOTONIC_TIME",
        return_value=monotonic_now + UNAVAILABLE_TRACK_SECONDS,
    ):
        async_fire_time_changed(
            hass, dt_util.utcnow() + timedelta(seconds=UNAVAILABLE_TRACK_SECONDS)
        )
        await hass.async_block_till_done()

    assert switchbot_device_went_unavailable is True
    switchbot_device_unavailable_cancel()


async def test_advertisment_interval_longer_than_adapter_stack_timeout_not_connectable(
    hass, caplog, enable_bluetooth, macos_adapter
):
    """Test device with a long advertisement interval that is not connectable not reaching the advertising interval."""
    start_monotonic_time = time.monotonic()
    switchbot_device = BLEDevice("44:44:33:11:23:45", "wohand")
    switchbot_adv = generate_advertisement_data(
        local_name="wohand", service_uuids=["cba20d00-224d-11e6-9fb8-0002a5d5c51b"]
    )
    switchbot_device_went_unavailable = False

    @callback
    def _switchbot_device_unavailable_callback(_address: str) -> None:
        """Switchbot device unavailable callback."""
        nonlocal switchbot_device_went_unavailable
        switchbot_device_went_unavailable = True

    for i in range(ADVERTISING_TIMES_NEEDED):
        inject_advertisement_with_time_and_source(
            hass,
            switchbot_device,
            switchbot_adv,
            start_monotonic_time + (i * ONE_HOUR_SECONDS),
            SOURCE_LOCAL,
        )

    switchbot_device_unavailable_cancel = async_track_unavailable(
        hass,
        _switchbot_device_unavailable_callback,
        switchbot_device.address,
        connectable=False,
    )

    monotonic_now = start_monotonic_time + (
        (ADVERTISING_TIMES_NEEDED - 1) * ONE_HOUR_SECONDS
    )
    with patch(
        "homeassistant.components.bluetooth.manager.MONOTONIC_TIME",
        return_value=monotonic_now + UNAVAILABLE_TRACK_SECONDS,
    ):
        async_fire_time_changed(
            hass, dt_util.utcnow() + timedelta(seconds=UNAVAILABLE_TRACK_SECONDS)
        )
        await hass.async_block_till_done()

    assert switchbot_device_went_unavailable is False
    switchbot_device_unavailable_cancel()


async def test_advertisment_interval_shorter_than_adapter_stack_timeout_adapter_change_not_connectable(
    hass, caplog, enable_bluetooth, macos_adapter
):
    """Test device with a short advertisement interval with an adapter change that is not connectable."""
    start_monotonic_time = time.monotonic()
    switchbot_device = BLEDevice("44:44:33:11:23:5C", "wohand")
    switchbot_adv = generate_advertisement_data(
        local_name="wohand",
        service_uuids=["cba20d00-224d-11e6-9fb8-0002a5d5c51b"],
        rssi=-100,
    )
    switchbot_device_went_unavailable = False

    @callback
    def _switchbot_device_unavailable_callback(_address: str) -> None:
        """Switchbot device unavailable callback."""
        nonlocal switchbot_device_went_unavailable
        switchbot_device_went_unavailable = True

    for i in range(ADVERTISING_TIMES_NEEDED):
        inject_advertisement_with_time_and_source(
            hass,
            switchbot_device,
            switchbot_adv,
            start_monotonic_time + (i * ONE_HOUR_SECONDS),
            "original",
        )

    switchbot_adv_better_rssi = generate_advertisement_data(
        local_name="wohand",
        service_uuids=["cba20d00-224d-11e6-9fb8-0002a5d5c51b"],
        rssi=-30,
    )
    for i in range(ADVERTISING_TIMES_NEEDED):
        inject_advertisement_with_time_and_source(
            hass,
            switchbot_device,
            switchbot_adv_better_rssi,
            start_monotonic_time + (i * 2),
            "new",
        )

    switchbot_device_unavailable_cancel = async_track_unavailable(
        hass,
        _switchbot_device_unavailable_callback,
        switchbot_device.address,
        connectable=False,
    )

    monotonic_now = start_monotonic_time + (
        (ADVERTISING_TIMES_NEEDED - 1) * ONE_HOUR_SECONDS
    )
    with patch(
        "homeassistant.components.bluetooth.manager.MONOTONIC_TIME",
        return_value=monotonic_now + UNAVAILABLE_TRACK_SECONDS,
    ):
        async_fire_time_changed(
            hass, dt_util.utcnow() + timedelta(seconds=UNAVAILABLE_TRACK_SECONDS)
        )
        await hass.async_block_till_done()

    assert switchbot_device_went_unavailable is True
    switchbot_device_unavailable_cancel()


async def test_advertisment_interval_longer_than_adapter_stack_timeout_adapter_change_not_connectable(
    hass, caplog, enable_bluetooth, macos_adapter
):
    """Test device with a long advertisement interval with an adapter change that is not connectable."""
    start_monotonic_time = time.monotonic()
    switchbot_device = BLEDevice("44:44:33:11:23:45", "wohand")
    switchbot_adv = generate_advertisement_data(
        local_name="wohand",
        service_uuids=["cba20d00-224d-11e6-9fb8-0002a5d5c51b"],
        rssi=-100,
    )
    switchbot_device_went_unavailable = False

    class FakeScanner(BaseHaScanner):
        """Fake scanner."""

        @property
        def discovered_devices_and_advertisement_data(
            self,
        ) -> dict[str, tuple[BLEDevice, AdvertisementData]]:
            """Return a list of discovered devices."""
            return {}

    scanner = FakeScanner(hass, "new", "fake_adapter")
    cancel_scanner = async_register_scanner(hass, scanner, False)

    @callback
    def _switchbot_device_unavailable_callback(_address: str) -> None:
        """Switchbot device unavailable callback."""
        nonlocal switchbot_device_went_unavailable
        switchbot_device_went_unavailable = True

    for i in range(ADVERTISING_TIMES_NEEDED):
        inject_advertisement_with_time_and_source_connectable(
            hass,
            switchbot_device,
            switchbot_adv,
            start_monotonic_time + (i * 2),
            "original",
            connectable=False,
        )

    switchbot_better_rssi_adv = generate_advertisement_data(
        local_name="wohand",
        service_uuids=["cba20d00-224d-11e6-9fb8-0002a5d5c51b"],
        rssi=-30,
    )
    for i in range(ADVERTISING_TIMES_NEEDED):
        inject_advertisement_with_time_and_source_connectable(
            hass,
            switchbot_device,
            switchbot_better_rssi_adv,
            start_monotonic_time + (i * ONE_HOUR_SECONDS),
            "new",
            connectable=False,
        )

    switchbot_device_unavailable_cancel = async_track_unavailable(
        hass,
        _switchbot_device_unavailable_callback,
        switchbot_device.address,
        connectable=False,
    )

    monotonic_now = start_monotonic_time + (
        (ADVERTISING_TIMES_NEEDED - 1) * ONE_HOUR_SECONDS
    )
    with patch(
        "homeassistant.components.bluetooth.manager.MONOTONIC_TIME",
        return_value=monotonic_now + UNAVAILABLE_TRACK_SECONDS,
    ):
        async_fire_time_changed(
            hass, dt_util.utcnow() + timedelta(seconds=UNAVAILABLE_TRACK_SECONDS)
        )
        await hass.async_block_till_done()

    assert switchbot_device_went_unavailable is False
    cancel_scanner()

    # Now that the scanner is gone we should go back to the stack default timeout
    with patch(
        "homeassistant.components.bluetooth.manager.MONOTONIC_TIME",
        return_value=monotonic_now + UNAVAILABLE_TRACK_SECONDS,
    ):
        async_fire_time_changed(
            hass, dt_util.utcnow() + timedelta(seconds=UNAVAILABLE_TRACK_SECONDS)
        )
        await hass.async_block_till_done()

    assert switchbot_device_went_unavailable is True

    switchbot_device_unavailable_cancel()


async def test_advertisment_interval_longer_increasing_than_adapter_stack_timeout_adapter_change_not_connectable(
    hass, caplog, enable_bluetooth, macos_adapter
):
    """Test device with a increasing advertisement interval with an adapter change that is not connectable."""
    start_monotonic_time = time.monotonic()
    switchbot_device = BLEDevice("44:44:33:11:23:45", "wohand")
    switchbot_adv = generate_advertisement_data(
        local_name="wohand", service_uuids=["cba20d00-224d-11e6-9fb8-0002a5d5c51b"]
    )
    switchbot_device_went_unavailable = False

    @callback
    def _switchbot_device_unavailable_callback(_address: str) -> None:
        """Switchbot device unavailable callback."""
        nonlocal switchbot_device_went_unavailable
        switchbot_device_went_unavailable = True

    for i in range(ADVERTISING_TIMES_NEEDED, 2 * ADVERTISING_TIMES_NEEDED):
        inject_advertisement_with_time_and_source(
            hass,
            switchbot_device,
            switchbot_adv,
            start_monotonic_time + (i**2),
            "new",
        )

    switchbot_device_unavailable_cancel = async_track_unavailable(
        hass,
        _switchbot_device_unavailable_callback,
        switchbot_device.address,
        connectable=False,
    )

    monotonic_now = start_monotonic_time + UNAVAILABLE_TRACK_SECONDS + 1
    with patch(
        "homeassistant.components.bluetooth.manager.MONOTONIC_TIME",
        return_value=monotonic_now + UNAVAILABLE_TRACK_SECONDS,
    ):
        async_fire_time_changed(
            hass, dt_util.utcnow() + timedelta(seconds=UNAVAILABLE_TRACK_SECONDS)
        )
        await hass.async_block_till_done()

    assert switchbot_device_went_unavailable is False
    switchbot_device_unavailable_cancel()
