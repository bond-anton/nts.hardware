"""Provide two-state and proportional actuators"""

from .actuator import Actuator, GPIOActuator
from .proportional_actuator import (
    ProportionalActuator,
    PWMProportionalActuator,
    GPIOProportionalActuator,
    HWPWMProportionalActuator,
)
