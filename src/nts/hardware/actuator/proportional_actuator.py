"""ProportionalActuator can change output value from 0 to 1"""

# from statemachine import StateMachine, State  # type: ignore
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


class GPIOProportionalActuator(ProportionalActuator):
    """Proportional actuator on top of gpiozero"""

    def __init__(self, pwm: PWMOutputDevice, label: str = "GPIO ACTUATOR", **kwargs):
        self.__pwm: PWMOutputDevice = pwm
        self.__pwm.value = 0
        super().__init__(label, **kwargs)

    def _apply_value(self) -> None:
        """Set PWM value"""
        pwm_value: float = self.value
        if self.normally_on:
            pwm_value = 1 - self.value
        self.__pwm.value = pwm_value

    def set_frequency(self, f: float) -> None:
        """Set PWM frequency"""
        if f < 0.1:
            f = 0.1
        elif f > 20e3:
            f = 20e3
        if not isinstance(self.__pwm.pin_factory, MockFactory):
            self.__pwm.frequency = f
        else:
            self.__pwm.frequency = None
        if self.verbose:
            print(f"{self.label}: PWM frequency set to {f:2.2g} Hz")


class HWPWMProportionalActuator(ProportionalActuator):
    """Proportional actuator on top of rpi-hardware-pwm"""

    def __init__(self, pwm: HardwarePWM, label: str = "HWPWM ACTUATOR", **kwargs):
        super().__init__(label, **kwargs)
        self.__pwm: HardwarePWM = pwm
        self._disabled: bool
        if self.normally_off:
            self.__pwm.stop()
            self._disabled = True
        else:
            self.__pwm.start(100)
            self._disabled = False

    def _apply_value(self) -> None:
        """Set PWM value"""
        pwm_value: float = self.value * 100
        if self.normally_on:
            pwm_value = 100 - self.value
        if pwm_value == 0:
            self.__pwm.stop()
            self._disabled = True
        else:
            if self._disabled:
                self.__pwm.start(pwm_value)
                self._disabled = False
            else:
                self.__pwm.change_duty_cycle(pwm_value)

    def set_frequency(self, f: float) -> None:
        """Set PWM frequency"""
        if f < 0.1:
            f = 0.1
        elif f > 20e3:
            f = 20e3
        self.__pwm.change_frequency(f)
        if self.verbose:
            print(f"{self.label}: PWM frequency set to {f:2.2g} Hz")
