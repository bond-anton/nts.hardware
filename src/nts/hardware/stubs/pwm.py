"""Stub module for rpi-hardware-pwm"""


class HardwarePWM:
    """HardwarePWM stub class"""

    def __init__(self, pwm_channel: int, hz: float, chip: int = 0) -> None:
        self._chip: int = chip
        self.pwm_channel = pwm_channel
        self._duty_cycle: float = 0
        self._hz: float = hz

    def change_duty_cycle(self, value: float) -> None:
        """set duty cycle to value"""
        self._duty_cycle = value

    def change_frequency(self, hz: float) -> None:
        """set pwm frequency"""
        self._hz = max(0.1, abs(hz))

    def start(self, initial_duty_cycle: float) -> None:
        """start pwm output"""
        self.change_duty_cycle(initial_duty_cycle)

    def stop(self) -> None:
        """stop pwm output"""
        self.change_duty_cycle(0)
