""" Testing Relay class """

import unittest
import logging
from gpiozero import Device, OutputDevice  # type: ignore
from gpiozero.pins.mock import MockFactory

try:
    from src.nts.hardware.actuator import GPIOActuator
except ModuleNotFoundError:
    from nts.hardware.actuator import GPIOActuator


Device.pin_factory = MockFactory()


class TestGPIORelay(unittest.TestCase):
    """
    Test Relay class.
    """

    pin = OutputDevice(17)

    def test_constructor(self) -> None:
        """
        test Relay constructor.
        """
        # pylint: disable=protected-access
        gpio_relay = GPIOActuator(self.pin)
        self.assertEqual(gpio_relay.label, "GPIO ACTUATOR")
        self.assertEqual(gpio_relay._is_normally_off(), True)
        self.assertEqual(gpio_relay.normally_off, True)
        self.assertEqual(gpio_relay.normally_on, False)
        self.assertEqual(gpio_relay.value, 0)

        gpio_relay = GPIOActuator(
            self.pin, label="MY RELAY", normally_off=False, log_level=logging.DEBUG
        )
        self.assertEqual(gpio_relay.label, "MY RELAY")
        self.assertEqual(gpio_relay._is_normally_off(), False)
        self.assertEqual(gpio_relay.normally_off, False)
        self.assertEqual(gpio_relay.normally_on, True)
        self.assertEqual(gpio_relay.value, 1)

        gpio_relay = GPIOActuator(
            self.pin, label="MY RELAY", normally_on=True, log_level=logging.DEBUG
        )
        self.assertEqual(gpio_relay.label, "MY RELAY")
        self.assertEqual(gpio_relay._is_normally_off(), False)
        self.assertEqual(gpio_relay.normally_off, False)
        self.assertEqual(gpio_relay.normally_on, True)
        self.assertEqual(gpio_relay.value, 1)

        gpio_relay = GPIOActuator(
            self.pin, label="MY RELAY", normally_on=False, log_level=logging.DEBUG
        )
        self.assertEqual(gpio_relay.label, "MY RELAY")
        self.assertEqual(gpio_relay._is_normally_off(), True)
        self.assertEqual(gpio_relay.normally_off, True)
        self.assertEqual(gpio_relay.normally_on, False)
        self.assertEqual(gpio_relay.value, 0)

    def test_value(self):
        """Test value property"""
        gpio_relay = GPIOActuator(self.pin, normally_off=True)
        self.assertEqual(gpio_relay.value, 0)
        self.assertEqual(self.pin.value, 0)
        self.assertEqual(gpio_relay.current_state, gpio_relay.off)
        gpio_relay.value = 1
        self.assertEqual(gpio_relay.value, 1)
        self.assertEqual(gpio_relay.current_state, gpio_relay.on)
        self.assertEqual(self.pin.value, 1)
        gpio_relay.value = 0
        self.assertEqual(gpio_relay.value, 0)
        self.assertEqual(gpio_relay.current_state, gpio_relay.off)
        self.assertEqual(self.pin.value, 0)
        gpio_relay.value = 0.5
        self.assertEqual(gpio_relay.value, 1)
        self.assertEqual(gpio_relay.current_state, gpio_relay.on)
        self.assertEqual(self.pin.value, 1)
        gpio_relay.value = 0.1
        self.assertEqual(gpio_relay.value, 0)
        self.assertEqual(gpio_relay.current_state, gpio_relay.off)
        self.assertEqual(self.pin.value, 0)
        gpio_relay.value = 0.6
        self.assertEqual(gpio_relay.value, 1)
        self.assertEqual(gpio_relay.current_state, gpio_relay.on)
        self.assertEqual(self.pin.value, 1)

        gpio_relay = GPIOActuator(self.pin, normally_on=True)
        self.assertEqual(gpio_relay.value, 1)
        self.assertEqual(self.pin.value, 0)
        self.assertEqual(gpio_relay.current_state, gpio_relay.on)
        gpio_relay.value = 0
        self.assertEqual(gpio_relay.value, 0)
        self.assertEqual(gpio_relay.current_state, gpio_relay.off)
        self.assertEqual(self.pin.value, 1)

    def test_switching(self):
        """Test switching on and off"""
        gpio_relay = GPIOActuator(self.pin, normally_off=True, log_level=logging.DEBUG)
        self.assertEqual(gpio_relay.value, 0)
        self.assertEqual(gpio_relay.current_state, gpio_relay.off)
        self.assertEqual(self.pin.value, 0)
        gpio_relay.switch_on()
        self.assertEqual(gpio_relay.value, 1)
        self.assertEqual(gpio_relay.current_state, gpio_relay.on)
        self.assertEqual(self.pin.value, 1)
        gpio_relay.switch_off()
        self.assertEqual(gpio_relay.value, 0)
        self.assertEqual(gpio_relay.current_state, gpio_relay.off)
        self.assertEqual(self.pin.value, 0)

        gpio_relay = GPIOActuator(self.pin, normally_on=True, log_level=logging.DEBUG)
        self.assertEqual(gpio_relay.value, 1)
        self.assertEqual(gpio_relay.current_state, gpio_relay.on)
        self.assertEqual(self.pin.value, 0)
        gpio_relay.switch_off()
        self.assertEqual(gpio_relay.value, 0)
        self.assertEqual(gpio_relay.current_state, gpio_relay.off)
        self.assertEqual(self.pin.value, 1)


if __name__ == "__main__":
    unittest.main()
