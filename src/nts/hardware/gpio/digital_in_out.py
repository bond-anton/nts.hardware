"""Digital inputs and outputs"""

from dataclasses import dataclass

from gpiozero import OutputDevice, DigitalInputDevice  # type: ignore
from gpiozero.pins.mock import MockFactory  # type: ignore


@dataclass
class RelayConfig:
    """Relay configuration"""

    pin_number: int
    label: str = "Relay"
    backend: str = "gpiozero"
    emulation: bool = True
    active_high: bool = True
    initial_value: bool = False


@dataclass
class ButtonConfig:
    """Button configuration"""

    pin_number: int
    label: str = "Button"
    backend: str = "gpiozero"
    emulation: bool = True
    pull_up: bool = True
    bounce_time: float = 0.0


def get_relay(relay: RelayConfig) -> OutputDevice:
    """Return GPIO output device"""
    if relay.backend == "gpiozero":
        return OutputDevice(
            relay.pin_number,
            active_high=relay.active_high,
            initial_value=relay.initial_value,
            pin_factory=MockFactory() if relay.emulation else None,
        )
    if relay.backend == "gpiod":
        raise NotImplementedError("GPIOD support not implemented yet.")
    raise NotImplementedError(f"{relay.backend} support not implemented yet.")


def get_button(button: ButtonConfig) -> DigitalInputDevice:
    """Return GPIO input device"""
    if button.backend == "gpiozero":
        return DigitalInputDevice(
            button.pin_number,
            pull_up=button.pull_up,
            bounce_time=button.bounce_time if button.bounce_time > 0 else None,
            pin_factory=MockFactory() if button.emulation else None,
        )
    if button.backend == "gpiod":
        raise NotImplementedError("GPIOD support not implemented yet.")
    raise NotImplementedError(f"{button.backend} support not implemented yet.")
