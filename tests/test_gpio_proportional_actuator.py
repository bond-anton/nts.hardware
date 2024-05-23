""" Testing GPIOProportionalActuator class """

import unittest
from gpiozero import Device, PWMOutputDevice  # type: ignore
from gpiozero.pins.mock import MockFactory

try:
    from src.nts.hardware.actuator import GPIOProportionalActuator
except ModuleNotFoundError:
    from nts.hardware.actuator import GPIOProportionalActuator


Device.pin_factory = MockFactory()


class TestGPIOProportionalActuator(unittest.TestCase):
    """
    Test GPIOProportionalActuator class.
    """

    pwm = PWMOutputDevice(12, frequency=None, pin_factory=MockFactory())

    def test_constructor(self) -> None:
        """
        test GPIOProportionalActuator constructor.
        """
        # pylint: disable=protected-access
        gpio_actuator = GPIOProportionalActuator(self.pwm)
        self.assertEqual(gpio_actuator.label, "GPIO ACTUATOR")
        self.assertEqual(gpio_actuator._is_normally_off(), True)
        self.assertEqual(gpio_actuator.normally_off, True)
        self.assertEqual(gpio_actuator.normally_on, False)
        self.assertEqual(gpio_actuator.value, 0)
        self.assertEqual(gpio_actuator.verbose, False)

        gpio_actuator = GPIOProportionalActuator(
            self.pwm, label="MY ACTUATOR", normally_off=False, verbose=True
        )
        self.assertEqual(gpio_actuator.label, "MY ACTUATOR")
        self.assertEqual(gpio_actuator._is_normally_off(), False)
        self.assertEqual(gpio_actuator.normally_off, False)
        self.assertEqual(gpio_actuator.normally_on, True)
        self.assertEqual(gpio_actuator.value, 1)
        self.assertEqual(gpio_actuator.verbose, True)

        gpio_actuator = GPIOProportionalActuator(
            self.pwm, label="MY ACTUATOR", normally_on=True, verbose=False
        )
        self.assertEqual(gpio_actuator.label, "MY ACTUATOR")
        self.assertEqual(gpio_actuator._is_normally_off(), False)
        self.assertEqual(gpio_actuator.normally_off, False)
        self.assertEqual(gpio_actuator.normally_on, True)
        self.assertEqual(gpio_actuator.value, 1)
        self.assertEqual(gpio_actuator.verbose, False)

        gpio_actuator = GPIOProportionalActuator(
            self.pwm, label="MY ACTUATOR", normally_on=False, verbose=True
        )
        self.assertEqual(gpio_actuator.label, "MY ACTUATOR")
        self.assertEqual(gpio_actuator._is_normally_off(), True)
        self.assertEqual(gpio_actuator.normally_off, True)
        self.assertEqual(gpio_actuator.normally_on, False)
        self.assertEqual(gpio_actuator.value, 0)
        self.assertEqual(gpio_actuator.verbose, True)

    def test_value(self):
        """Test value property"""
        gpio_actuator = GPIOProportionalActuator(self.pwm, normally_off=True)
        self.assertEqual(gpio_actuator.value, 0)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.off)
        gpio_actuator.value = 1
        self.assertEqual(gpio_actuator.value, 1)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)
        gpio_actuator.value = 0
        self.assertEqual(gpio_actuator.value, 0)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.off)
        gpio_actuator.value = 0.5
        self.assertEqual(gpio_actuator.value, 0.5)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)
        gpio_actuator.value = 0.1
        self.assertEqual(gpio_actuator.value, 0.1)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)
        gpio_actuator.value = 1.1
        self.assertEqual(gpio_actuator.value, 1)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)
        gpio_actuator.value = -1
        self.assertEqual(gpio_actuator.value, 0)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.off)

        gpio_actuator = GPIOProportionalActuator(self.pwm, normally_on=True)
        self.assertEqual(gpio_actuator.value, 1)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)
        gpio_actuator.value = 0
        self.assertEqual(gpio_actuator.value, 0)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.off)
        gpio_actuator.value = 0
        self.assertEqual(gpio_actuator.value, 0)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.off)
        gpio_actuator.value = 0.5
        self.assertEqual(gpio_actuator.value, 0.5)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)
        gpio_actuator.value = 0.1
        self.assertEqual(gpio_actuator.value, 0.1)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)
        gpio_actuator.value = 1.1
        self.assertEqual(gpio_actuator.value, 1)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)
        gpio_actuator.value = -1
        self.assertEqual(gpio_actuator.value, 0)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.off)

    def test_switching(self):
        """Test switching on and off"""
        gpio_actuator = GPIOProportionalActuator(
            self.pwm, normally_off=True, verbose=True
        )
        self.assertEqual(gpio_actuator.value, 0)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.off)
        gpio_actuator.switch_on()
        self.assertEqual(gpio_actuator.value, 1)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)
        gpio_actuator.value = 0.1
        self.assertEqual(gpio_actuator.value, 0.1)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)
        gpio_actuator.switch_off()
        self.assertEqual(gpio_actuator.value, 0)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.off)
        gpio_actuator.switch_on()
        self.assertEqual(gpio_actuator.value, 0.1)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)

        gpio_actuator = GPIOProportionalActuator(
            self.pwm, normally_off=False, verbose=True
        )
        self.assertEqual(gpio_actuator.value, 1)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.on)
        gpio_actuator.switch_off()
        self.assertEqual(gpio_actuator.value, 0)
        self.assertEqual(gpio_actuator.current_state, gpio_actuator.off)

    def test_change_frequency(self):
        """test frequency change"""
        gpio_actuator = GPIOProportionalActuator(
            self.pwm, normally_off=True, verbose=True
        )
        gpio_actuator.set_frequency(2000)


if __name__ == "__main__":
    unittest.main()
