"""ProportionalActuator can change output value from 0 to 1"""

from typing import Union
from gpiozero import PWMOutputDevice  # type: ignore
from gpiozero.pins.mock import MockFactory  # type: ignore

try:
    from rpi_hardware_pwm import HardwarePWM  # type: ignore
except ModuleNotFoundError:
    from nts.hardware.stubs.pwm import HardwarePWM  # type: ignore

from .actuator import Actuator


class ProportionalActuator(Actuator):
    """
    ProportionalActuator is a state machine with three states initialization->on<->off.
    The off state value is always zero, and the on state can have value in the range from 0 to 1.
    """

    def _check_value(self, value: float) -> float:
        if value < 0:
            return 0
        if value > 1:
            return 1
        return value


class PWMProportionalActuator(ProportionalActuator):
    """ProportionalActuator with PWM output"""

    def __init__(self, label: str = "PWM ACTUATOR", **kwargs) -> None:
        self.__pwm_range: tuple[float, float] = (0.0, 1.0)
        self.__pwm_value: float = 0
        self.__freq_range: tuple[float, float] = (1e-3, 1e6)
        super().__init__(label, **kwargs)
        self._apply_value()

    @property
    def pwm_range(self) -> tuple[float, float]:
        """Range of allowed PWM output"""
        return self.__pwm_range

    @pwm_range.setter
    def pwm_range(self, new_range: Union[tuple[float, float], list[float]]) -> None:
        self.__pwm_range = (
            min(1.0, max(0.0, min(new_range))),
            min(1.0, max(new_range)),
        )
        self._apply_value()

    @property
    def frequency_range(self) -> tuple[float, float]:
        """Range of allowed PWM output"""
        return self.__freq_range

    @frequency_range.setter
    def frequency_range(
        self, new_range: Union[tuple[float, float], list[float]]
    ) -> None:
        self.__freq_range = (
            min(1e6, max(1.0e-3, min(new_range))),
            min(1.0e6, max(new_range)),
        )

    @property
    def pwm_value(self) -> float:
        """pwm_value property"""
        return self.__pwm_value

    @pwm_value.setter
    def pwm_value(self, val: float) -> None:
        self.__pwm_value = (
            self.pwm_range[0] + (self.pwm_range[1] - self.pwm_range[0]) * val
        )

    def _apply_value(self) -> None:
        """Set PWM value"""
        pwm_value: float = self.value
        if self.normally_on:
            pwm_value = 1 - self.value
        self.pwm_value = pwm_value
        self._set_pwm()

    def _set_pwm(self) -> None:
        """set PWM to self.__pwm_value"""

    def set_frequency(self, f: float) -> None:
        """Set PWM frequency"""
        if f < self.__freq_range[0]:
            f = self.__freq_range[0]
        elif f > self.__freq_range[1]:
            f = self.__freq_range[1]
        self._set_freq(f)
        self.logger.debug("%s: PWM frequency set to %2.2g Hz", self.label, f)

    def _set_freq(self, f: float) -> None:
        """set pwm freq method"""


class GPIOProportionalActuator(PWMProportionalActuator):
    """Proportional actuator on top of gpiozero"""

    def __init__(
        self, pwm: PWMOutputDevice, label: str = "GPIO ACTUATOR", **kwargs
    ) -> None:
        self.__pwm: PWMOutputDevice = pwm
        self.__pwm.value = 0
        super().__init__(label, **kwargs)

    def _set_pwm(self) -> None:
        self.__pwm.value = self.pwm_value

    def _set_freq(self, f: float) -> None:
        """Set PWM frequency"""
        if not isinstance(self.__pwm.pin_factory, MockFactory):
            self.__pwm.frequency = f
        else:
            self.__pwm.frequency = None


class HWPWMProportionalActuator(PWMProportionalActuator):
    """Proportional actuator on top of rpi-hardware-pwm"""

    def __init__(
        self, pwm: HardwarePWM, label: str = "HWPWM ACTUATOR", **kwargs
    ) -> None:
        self.__pwm: HardwarePWM = pwm
        self.__pwm.stop()
        self._disabled: bool = True
        super().__init__(label, **kwargs)

    def _set_pwm(self) -> None:
        """Set PWM value"""
        if self.pwm_value == 0:
            self.__pwm.stop()
            self._disabled = True
        else:
            if self._disabled:
                self.__pwm.start(self.pwm_value * 100)
                self._disabled = False
            else:
                self.__pwm.change_duty_cycle(self.pwm_value * 100)

    def _set_freq(self, f: float) -> None:
        """Set PWM frequency"""
        self.__pwm.change_frequency(f)
