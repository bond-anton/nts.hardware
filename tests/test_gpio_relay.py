""" Testing Relay class """

import unittest
from gpiozero import Device, OutputDevice  # type: ignore
from gpiozero.pins.mock import MockFactory

try:
    from src.nts.hardware.relay import GPIORelay
except ModuleNotFoundError:
    from nts.hardware.relay import GPIORelay


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
        gpio_relay = GPIORelay(self.pin)
        self.assertEqual(gpio_relay.label, "GPIO Relay")
        self.assertEqual(gpio_relay._is_normally_off(), True)
        self.assertEqual(gpio_relay.normally_off, True)
        self.assertEqual(gpio_relay.normally_on, False)
        self.assertEqual(gpio_relay.value, 0)
        self.assertEqual(gpio_relay.verbose, False)

        gpio_relay = GPIORelay(
            self.pin, label="MY RELAY", normally_off=False, verbose=True
        )
        self.assertEqual(gpio_relay.label, "MY RELAY")
        self.assertEqual(gpio_relay._is_normally_off(), False)
        self.assertEqual(gpio_relay.normally_off, False)
        self.assertEqual(gpio_relay.normally_on, True)
        self.assertEqual(gpio_relay.value, 1)
        self.assertEqual(gpio_relay.verbose, True)

        gpio_relay = GPIORelay(
            self.pin, label="MY RELAY", normally_on=True, verbose=False
        )
        self.assertEqual(gpio_relay.label, "MY RELAY")
        self.assertEqual(gpio_relay._is_normally_off(), False)
        self.assertEqual(gpio_relay.normally_off, False)
        self.assertEqual(gpio_relay.normally_on, True)
        self.assertEqual(gpio_relay.value, 1)
        self.assertEqual(gpio_relay.verbose, False)

        gpio_relay = GPIORelay(
            self.pin, label="MY RELAY", normally_on=False, verbose=True
        )
        self.assertEqual(gpio_relay.label, "MY RELAY")
        self.assertEqual(gpio_relay._is_normally_off(), True)
        self.assertEqual(gpio_relay.normally_off, True)
        self.assertEqual(gpio_relay.normally_on, False)
        self.assertEqual(gpio_relay.value, 0)
        self.assertEqual(gpio_relay.verbose, True)

    def test_value(self):
        """Test value property"""
        gpio_relay = GPIORelay(self.pin)
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

    def test_switching(self):
        """Test switching on and off"""
        gpio_relay = GPIORelay(self.pin, verbose=True)
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
