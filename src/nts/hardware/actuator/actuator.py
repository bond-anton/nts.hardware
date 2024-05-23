"""Actuator can change output value from 0 to 1"""

from statemachine import StateMachine, State  # type: ignore
from gpiozero import OutputDevice  # type: ignore


class Actuator(StateMachine):
    """
    Actuator is a state machine with three states initialization->on<->off.
    The off state value is always zero, and the on state is 1.
    """

    initialization = State(initial=True)
    off = State()
    on = State()

    initialize = initialization.to(off, cond="_is_normally_off") | initialization.to(
        on, unless="_is_normally_off"
    )
    change_value = (
        off.to(off, unless="_is_on")
        | off.to(on, cond="_is_on")
        | on.to(on, cond="_is_on")
        | on.to(off, unless="_is_on")
    )

    def __init__(self, label: str = "ACTUATOR", **kwargs) -> None:
        self.__label: str = str(label)
        self.__normally_off = True
        self._value: float = 0  # value = 0 - Valve closed, value = 1 - Valve opened
        if "normally_off" in kwargs:
            self.__normally_off = bool(kwargs.pop("normally_off"))
        if "normally_on" in kwargs:
            self.__normally_off = not bool(kwargs.pop("normally_on"))
        if not self.__normally_off:
            self._value = 1
        self._value_stored: float = self._value
        self.__verbose: bool = False
        if "verbose" in kwargs:
            self.__verbose = bool(kwargs.pop("verbose"))

        super().__init__(**kwargs)

        if self.current_state == self.initialization:
            self.send("initialize")

    @property
    def label(self) -> str:
        """Relay label string"""
        return self.__label

    @label.setter
    def label(self, label: str) -> None:
        """Label setter"""
        self.__label = str(label)

    def _is_normally_off(self) -> bool:
        """check that the Relay is normally off"""
        return self.__normally_off

    @property
    def normally_off(self) -> bool:
        """Normally off status property"""
        return self.__normally_off

    @property
    def normally_on(self) -> bool:
        """Normally on status property"""
        return not self.__normally_off

    @property
    def value(self) -> float:
        """Numeric value of actuator"""
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        """Value setter"""
        new_value: float = self._check_value(value)
        if self._value != new_value:
            self._value = new_value
            self.send("change_value")

    def _check_value(self, value: float) -> float:
        if value < 0.5:
            return 0
        return 1

    def _is_on(self):
        """Check if the actuator has positive value"""
        return self.value > 0

    @property
    def verbose(self) -> bool:
        """Verbose property"""
        return self.__verbose

    @verbose.setter
    def verbose(self, verbose: bool) -> None:
        """Verbose property setter"""
        self.__verbose = bool(verbose)

    def before_change_value(
        self, event: str, source: State, target: State, message: str = ""
    ) -> None:
        """Preparations before value change"""
        if self.verbose:
            message = ". " + message if message else ""
            print(
                f"[{event.upper():^10s}] {self.label} is going to {event} "
                f"from {source.id.upper()} to {target.id.upper()}{message}"
            )

    def on_change_value(
        self, event: str, source: State, target: State, message: str = ""
    ) -> None:
        """value change action"""
        self._apply_value()
        if self.verbose:
            message = f". {message}." if message else ""
            print(
                f"[{event.upper():^10s}] {self.label} state changed "
                f"from {source.id.upper()} to {target.id.upper()}{message}"
            )
            print(f"[{event.upper():^10s}] {self.label} value is {self.value}")

    def on_enter_off(self, event: str, state: State) -> None:
        """Switch off action"""
        if self.verbose:
            print(f"[{event.upper():^10s}] {self.label} is {state.id.upper()}.")

    def on_enter_on(self, event: str, state: State) -> None:
        """Switch on action"""
        if self.verbose:
            print(f"[{event.upper():^10s}] {self.label} is {state.id.upper()}.")

    def _apply_value(self) -> None:
        """Value change function to be reimplemented"""

    def switch_off(self) -> None:
        """Switch off command"""
        if self.current_state == self.on:
            self._value_stored = self._value
            self._value = 0.0
            self.send("change_value")

    def switch_on(self) -> None:
        """Switch on command"""
        if self.current_state == self.off:
            if self._value_stored > 0:
                self._value = self._value_stored
            else:
                self._value = 1
            self.send("change_value")


class GPIOActuator(Actuator):
    """Actuator on top of gpiozero"""

    def __init__(
        self, gpio_relay: OutputDevice, label: str = "GPIO ACTUATOR", **kwargs
    ):
        self.__gpio_relay: OutputDevice = gpio_relay
        self.__gpio_relay.off()
        super().__init__(label, **kwargs)

    def _apply_value(self) -> None:
        """Set GPIO pin value"""
        value: float
        if self.normally_on:
            value = 1 - self.value
        else:
            value = self.value
        if value < 0.5:
            self.__gpio_relay.off()
        else:
            self.__gpio_relay.on()
