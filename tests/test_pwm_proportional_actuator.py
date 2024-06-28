""" Testing PWMProportionalActuator class """

import unittest
import logging

try:
    from src.nts.hardware.actuator import PWMProportionalActuator
except ModuleNotFoundError:
    from nts.hardware.actuator import PWMProportionalActuator


class TestPWMProportionalActuator(unittest.TestCase):
    """
    Test PWMProportionalActuator class.
    """

    def test_constructor(self) -> None:
        """
        test PWMProportionalActuator constructor.
        """
        # pylint: disable=protected-access
        pwm_actuator = PWMProportionalActuator()
        self.assertEqual(pwm_actuator.label, "PWM ACTUATOR")
        self.assertEqual(pwm_actuator._is_normally_off(), True)
        self.assertEqual(pwm_actuator.normally_off, True)
        self.assertEqual(pwm_actuator.normally_on, False)
        self.assertEqual(pwm_actuator.value, 0)
        self.assertEqual(pwm_actuator.pwm_range, (0.0, 1.0))
        self.assertEqual(pwm_actuator.pwm_value, 0.0)
        self.assertEqual(pwm_actuator.frequency_range, (1e-3, 1e6))

        pwm_actuator = PWMProportionalActuator(
            label="MY ACTUATOR", normally_off=False, log_level=logging.DEBUG
        )
        self.assertEqual(pwm_actuator.label, "MY ACTUATOR")
        self.assertEqual(pwm_actuator._is_normally_off(), False)
        self.assertEqual(pwm_actuator.normally_off, False)
        self.assertEqual(pwm_actuator.normally_on, True)
        self.assertEqual(pwm_actuator.value, 1)

        pwm_actuator = PWMProportionalActuator(
            label="MY ACTUATOR", normally_on=True, log_level=logging.DEBUG
        )
        self.assertEqual(pwm_actuator.label, "MY ACTUATOR")
        self.assertEqual(pwm_actuator._is_normally_off(), False)
        self.assertEqual(pwm_actuator.normally_off, False)
        self.assertEqual(pwm_actuator.normally_on, True)
        self.assertEqual(pwm_actuator.value, 1)

        pwm_actuator = PWMProportionalActuator(
            label="MY ACTUATOR", normally_on=False, log_level=logging.DEBUG
        )
        self.assertEqual(pwm_actuator.label, "MY ACTUATOR")
        self.assertEqual(pwm_actuator._is_normally_off(), True)
        self.assertEqual(pwm_actuator.normally_off, True)
        self.assertEqual(pwm_actuator.normally_on, False)
        self.assertEqual(pwm_actuator.value, 0)

    def test_frequency_range(self):
        """test frequency_range property"""
        pwm_actuator = PWMProportionalActuator()
        self.assertEqual(pwm_actuator.frequency_range, (1e-3, 1e6))
        pwm_actuator.frequency_range = (1.0, 3e3)
        self.assertEqual(pwm_actuator.frequency_range, (1.0, 3e3))
        pwm_actuator.frequency_range = [10.0, 30e3]
        self.assertEqual(pwm_actuator.frequency_range, (10.0, 30e3))
        pwm_actuator.frequency_range = [20e3, 15.0]
        self.assertEqual(pwm_actuator.frequency_range, (15.0, 20e3))
        pwm_actuator.frequency_range = [-20, 150.0e3]
        self.assertEqual(pwm_actuator.frequency_range, (1e-3, 150e3))
        pwm_actuator.frequency_range = [-20, 2.0e6]
        self.assertEqual(pwm_actuator.frequency_range, (1e-3, 1e6))
        pwm_actuator.frequency_range = [3e6, 2.0e6]
        self.assertEqual(pwm_actuator.frequency_range, (1e6, 1e6))

    def test_pwm_range(self):
        """test pwm_range property"""
        pwm_actuator = PWMProportionalActuator()
        self.assertEqual(pwm_actuator.pwm_range, (0, 1))
        pwm_actuator.pwm_range = (0.2, 0.9)
        self.assertEqual(pwm_actuator.pwm_range, (0.2, 0.9))
        pwm_actuator.pwm_range = [0.1, 0.8]
        self.assertEqual(pwm_actuator.pwm_range, (0.1, 0.8))
        pwm_actuator.pwm_range = [20e3, 15.0]
        self.assertEqual(pwm_actuator.pwm_range, (1.0, 1.0))
        pwm_actuator.pwm_range = [-20, 150.0e3]
        self.assertEqual(pwm_actuator.pwm_range, (0, 1))
        pwm_actuator.pwm_range = [-20, 0.8]
        self.assertEqual(pwm_actuator.pwm_range, (0, 0.8))

    def test_set_frequency(self):
        """test set_frequency method"""
        pwm_actuator = PWMProportionalActuator()
        pwm_actuator.set_frequency(-2e7)
        pwm_actuator.set_frequency(2e7)
        pwm_actuator.set_frequency(1e3)

    def test_value_norm_off(self):
        """Test value property"""
        pwm_actuator = PWMProportionalActuator(normally_off=True)
        self.assertEqual(pwm_actuator.value, 0)
        self.assertEqual(pwm_actuator.pwm_value, 0)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.off)
        pwm_actuator.value = 1
        self.assertEqual(pwm_actuator.value, 1)
        self.assertEqual(pwm_actuator.pwm_value, 1)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.on)
        pwm_actuator.value = 0
        self.assertEqual(pwm_actuator.value, 0)
        self.assertEqual(pwm_actuator.pwm_value, 0)
        pwm_actuator.value = 0.5
        self.assertEqual(pwm_actuator.value, 0.5)
        self.assertEqual(pwm_actuator.pwm_value, 0.5)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.on)
        pwm_actuator.value = 1.1
        self.assertEqual(pwm_actuator.value, 1)
        self.assertEqual(pwm_actuator.pwm_value, 1)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.on)
        pwm_actuator.value = -1
        self.assertEqual(pwm_actuator.value, 0)
        self.assertEqual(pwm_actuator.pwm_value, 0)
        pwm_actuator.pwm_range = (0.2, 0.6)
        self.assertEqual(pwm_actuator.pwm_value, 0.2)
        pwm_actuator.value = 1
        self.assertEqual(pwm_actuator.value, 1)
        self.assertEqual(pwm_actuator.pwm_value, 0.6)
        pwm_actuator.value = 0.5
        self.assertEqual(pwm_actuator.value, 0.5)
        self.assertEqual(pwm_actuator.pwm_value, 0.4)

    def test_value_norm_on(self):
        """Test value property"""
        pwm_actuator = PWMProportionalActuator(normally_on=True)
        self.assertEqual(pwm_actuator.value, 1)
        self.assertEqual(pwm_actuator.pwm_value, 0)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.on)
        pwm_actuator.value = 0
        self.assertEqual(pwm_actuator.value, 0)
        self.assertEqual(pwm_actuator.pwm_value, 1)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.off)
        pwm_actuator.value = 0.5
        self.assertEqual(pwm_actuator.value, 0.5)
        self.assertEqual(pwm_actuator.pwm_value, 0.5)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.on)
        pwm_actuator.value = 0.1
        self.assertEqual(pwm_actuator.value, 0.1)
        self.assertEqual(pwm_actuator.pwm_value, 0.9)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.on)
        pwm_actuator.value = 1.1
        self.assertEqual(pwm_actuator.value, 1)
        self.assertEqual(pwm_actuator.pwm_value, 0)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.on)
        pwm_actuator.value = -1
        self.assertEqual(pwm_actuator.value, 0)
        self.assertEqual(pwm_actuator.pwm_value, 1)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.off)

    def test_switching(self):
        """Test switching on and off"""
        pwm_actuator = PWMProportionalActuator(
            normally_off=True, log_level=logging.DEBUG
        )
        self.assertEqual(pwm_actuator.value, 0)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.off)
        pwm_actuator.switch_on()
        self.assertEqual(pwm_actuator.value, 1)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.on)
        pwm_actuator.value = 0.1
        self.assertEqual(pwm_actuator.value, 0.1)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.on)
        pwm_actuator.switch_off()
        self.assertEqual(pwm_actuator.value, 0)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.off)
        pwm_actuator.switch_on()
        self.assertEqual(pwm_actuator.value, 0.1)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.on)

        pwm_actuator = PWMProportionalActuator(
            normally_off=False, log_level=logging.DEBUG
        )
        self.assertEqual(pwm_actuator.value, 1)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.on)
        pwm_actuator.switch_off()
        self.assertEqual(pwm_actuator.value, 0)
        self.assertEqual(pwm_actuator.current_state, pwm_actuator.off)

    def test_change_frequency(self):
        """test frequency change"""
        gpio_actuator = PWMProportionalActuator(
            normally_off=True, log_level=logging.DEBUG
        )
        gpio_actuator.set_frequency(2000)


if __name__ == "__main__":
    unittest.main()
