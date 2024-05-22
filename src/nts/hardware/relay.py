"""Relay is a simple on-off switch"""

from typing import Union
from statemachine import StateMachine, State  # type: ignore
from gpiozero import OutputDevice  # type: ignore


class Relay(StateMachine):
    """Relay is a state machine with three states initialization->on<->off"""

    initialization = State(initial=True)
    off = State()
    on = State()

    initialize = initialization.to(off, cond="_is_normally_off") | initialization.to(
        on, unless="_is_normally_off"
    )
    switch = off.to(on) | on.to(off)

    def __init__(self, label: str = "RELAY", **kwargs) -> None:
        self.__label: str = str(label)
        self.__normally_off = True
        self.__value: int = 0  # value = 0 - Valve closed, value = 1 - Valve opened
        if "normally_off" in kwargs:
            self.__normally_off = bool(kwargs.pop("normally_off"))
        if "normally_on" in kwargs:
            self.__normally_off = not bool(kwargs.pop("normally_on"))
        if not self.__normally_off:
            self.__value = 1
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
    def value(self) -> int:
        """Numeric value of a state 1=ON 0=OFF"""
        return int(self.__value)

    @value.setter
    def value(self, value: Union[int, float]) -> None:
        """Value setter"""
        new_value: int
        if value < 0.5:
            new_value = 0
        else:
            new_value = 1
        if self.__value != new_value:
            self.send("switch")

    @property
    def verbose(self) -> bool:
        """Verbose property"""
        return self.__verbose

    @verbose.setter
    def verbose(self, verbose: bool) -> None:
        """Verbose property setter"""
        self.__verbose = bool(verbose)

    def before_switch(
        self, event: str, source: State, target: State, message: str = ""
    ) -> None:
        """Preparations before state switching"""
        if self.verbose:
            message = ". " + message if message else ""
            print(
                f"[{event.upper():^10s}] {self.label} is going to {event} "
                f"from {source.id.upper()} to {target.id.upper()}{message}"
            )

    def on_enter_off(self, event: str, state: State) -> None:
        """Switch off action"""
        self._turn_off()
        self.__value = 0
        if self.verbose:
            print(f"[{event.upper():^10s}] {self.label} is {state.id.upper()}.")

    def on_enter_on(self, event: str, state: State) -> None:
        """Switch on action"""
        self._turn_on()
        self.__value = 1
        if self.verbose:
            print(f"[{event.upper():^10s}] {self.label} is {state.id.upper()}.")

    def _turn_on(self) -> None:
        """Turn on function to be reimplemented"""

    def _turn_off(self) -> None:
        """Turn off function to be reimplemented"""

    def switch_off(self) -> None:
        """Switch off command"""
        if self.current_state == self.on:
            self.send("switch")

    def switch_on(self) -> None:
        """Switch on command"""
        if self.current_state == self.off:
            self.send("switch")


class GPIORelay(Relay):
    """GPIO pin controlled relay"""

    def __init__(
        self,
        gpio_relay: OutputDevice,
        label: str = "GPIO Relay",
        **kwargs,
    ) -> None:
        self.__gpio_relay: OutputDevice = gpio_relay
        super().__init__(label, **kwargs)

    def _turn_on(self) -> None:
        """turn GPIO pin output on"""
        self.__gpio_relay.on()

    def _turn_off(self) -> None:
        """turn GPIO pin output off"""
        self.__gpio_relay.off()
