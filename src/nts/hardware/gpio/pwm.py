"""PWM output"""

from typing import Union
from dataclasses import dataclass

from gpiozero import PWMOutputDevice  # type: ignore
from gpiozero.pins.mock import MockFactory  # type: ignore

try:
    from rpi_hardware_pwm import HardwarePWM  # type: ignore
except ModuleNotFoundError:
    from nts.hardware.stubs.pwm import HardwarePWM  # type: ignore


@dataclass
class PWMConfig:
    """PWM configuration"""

    # pylint: disable=too-many-instance-attributes
    # Nine is reasonable in this case.

    pin_number: int = 12
    chip: int = 0
    channel: int = 0
    label: str = "PWM"
    backend: str = "gpiozero"
    emulation: bool = True
    frequency: int = 8000
    active_high: bool = True
    initial_value: float = 0.0


def get_pwm(pwm: PWMConfig) -> Union[PWMOutputDevice, HardwarePWM]:
    """Return PWM output device"""
    if pwm.backend == "gpiozero":
        return PWMOutputDevice(
            pwm.pin_number,
            frequency=None if pwm.emulation else pwm.frequency,
            active_high=pwm.active_high,
            initial_value=pwm.initial_value,
            pin_factory=MockFactory() if pwm.emulation else None,
        )
    if pwm.backend == "rpi_hardware_pwm":
        return HardwarePWM(pwm_channel=pwm.channel, hz=pwm.frequency, chip=pwm.chip)
    if pwm.backend == "gpiod":
        raise NotImplementedError("GPIOD support not implemented yet.")
    raise NotImplementedError(f"{pwm.backend} support not implemented yet.")
