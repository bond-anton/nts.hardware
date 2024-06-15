""" Testing HWPWMProportionalActuator class """

import unittest

# pylint: disable=ungrouped-imports
# Conditional ungrouped import is reasonable in this case.

try:
    from rpi_hardware_pwm import HardwarePWM  # type: ignore
except ModuleNotFoundError:
    try:
        from src.nts.hardware.stubs.pwm import HardwarePWM
    except ModuleNotFoundError:
        from nts.hardware.stubs.pwm import HardwarePWM
try:
    from src.nts.hardware.actuator import HWPWMProportionalActuator
except ModuleNotFoundError:
    from nts.hardware.actuator import HWPWMProportionalActuator


class TestHWPWMProportionalActuator(unittest.TestCase):
    """
    Test HWPWMProportionalActuator class.
    """

    pwm = HardwarePWM(0, 4000, 0)

    def test_constructor(self) -> None:
        """
        test HWPWMProportionalActuator constructor.
        """
        # pylint: disable=protected-access
        hwpwm_actuator = HWPWMProportionalActuator(self.pwm)
        self.assertEqual(hwpwm_actuator.label, "HWPWM ACTUATOR")
        self.assertEqual(hwpwm_actuator._is_normally_off(), True)
        self.assertEqual(hwpwm_actuator.normally_off, True)
        self.assertEqual(hwpwm_actuator.normally_on, False)
        self.assertEqual(hwpwm_actuator.value, 0)
        self.assertEqual(hwpwm_actuator.verbose, False)

        hwpwm_actuator = HWPWMProportionalActuator(
            self.pwm, label="MY ACTUATOR", normally_off=False, verbose=True
        )
        self.assertEqual(hwpwm_actuator.label, "MY ACTUATOR")
        self.assertEqual(hwpwm_actuator._is_normally_off(), False)
        self.assertEqual(hwpwm_actuator.normally_off, False)
        self.assertEqual(hwpwm_actuator.normally_on, True)
        self.assertEqual(hwpwm_actuator.value, 1)
        self.assertEqual(hwpwm_actuator.verbose, True)

        hwpwm_actuator = HWPWMProportionalActuator(
            self.pwm, label="MY ACTUATOR", normally_on=True, verbose=False
        )
        self.assertEqual(hwpwm_actuator.label, "MY ACTUATOR")
        self.assertEqual(hwpwm_actuator._is_normally_off(), False)
        self.assertEqual(hwpwm_actuator.normally_off, False)
        self.assertEqual(hwpwm_actuator.normally_on, True)
        self.assertEqual(hwpwm_actuator.value, 1)
        self.assertEqual(hwpwm_actuator.verbose, False)

        hwpwm_actuator = HWPWMProportionalActuator(
            self.pwm, label="MY ACTUATOR", normally_on=False, verbose=True
        )
        self.assertEqual(hwpwm_actuator.label, "MY ACTUATOR")
        self.assertEqual(hwpwm_actuator._is_normally_off(), True)
        self.assertEqual(hwpwm_actuator.normally_off, True)
        self.assertEqual(hwpwm_actuator.normally_on, False)
        self.assertEqual(hwpwm_actuator.value, 0)
        self.assertEqual(hwpwm_actuator.verbose, True)

    def test_value(self):
        """Test value property"""
        hwpwm_actuator = HWPWMProportionalActuator(self.pwm, normally_off=True)
        self.assertEqual(hwpwm_actuator.value, 0)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.off)
        hwpwm_actuator.value = 1
        self.assertEqual(hwpwm_actuator.value, 1)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)
        hwpwm_actuator.value = 0
        self.assertEqual(hwpwm_actuator.value, 0)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.off)
        hwpwm_actuator.value = 0.5
        self.assertEqual(hwpwm_actuator.value, 0.5)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)
        hwpwm_actuator.value = 0.1
        self.assertEqual(hwpwm_actuator.value, 0.1)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)
        hwpwm_actuator.value = 1.1
        self.assertEqual(hwpwm_actuator.value, 1)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)
        hwpwm_actuator.value = -1
        self.assertEqual(hwpwm_actuator.value, 0)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.off)

        hwpwm_actuator = HWPWMProportionalActuator(self.pwm, normally_on=True)
        self.assertEqual(hwpwm_actuator.value, 1)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)
        hwpwm_actuator.value = 0
        self.assertEqual(hwpwm_actuator.value, 0)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.off)
        hwpwm_actuator.value = 0
        self.assertEqual(hwpwm_actuator.value, 0)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.off)
        hwpwm_actuator.value = 0.5
        self.assertEqual(hwpwm_actuator.value, 0.5)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)
        hwpwm_actuator.value = 0.1
        self.assertEqual(hwpwm_actuator.value, 0.1)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)
        hwpwm_actuator.value = 1.1
        self.assertEqual(hwpwm_actuator.value, 1)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)
        hwpwm_actuator.value = -1
        self.assertEqual(hwpwm_actuator.value, 0)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.off)

    def test_switching(self):
        """Test switching on and off"""
        hwpwm_actuator = HWPWMProportionalActuator(
            self.pwm, normally_off=True, verbose=True
        )
        self.assertEqual(hwpwm_actuator.value, 0)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.off)
        hwpwm_actuator.switch_on()
        self.assertEqual(hwpwm_actuator.value, 1)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)
        hwpwm_actuator.value = 0.1
        self.assertEqual(hwpwm_actuator.value, 0.1)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)
        hwpwm_actuator.switch_off()
        self.assertEqual(hwpwm_actuator.value, 0)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.off)
        hwpwm_actuator.switch_on()
        self.assertEqual(hwpwm_actuator.value, 0.1)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)

        hwpwm_actuator = HWPWMProportionalActuator(
            self.pwm, normally_off=False, verbose=True
        )
        self.assertEqual(hwpwm_actuator.value, 1)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.on)
        hwpwm_actuator.switch_off()
        self.assertEqual(hwpwm_actuator.value, 0)
        self.assertEqual(hwpwm_actuator.current_state, hwpwm_actuator.off)

    def test_change_frequency(self):
        """Test frequency change"""
        hwpwm_actuator = HWPWMProportionalActuator(
            self.pwm, normally_off=True, verbose=True
        )
        hwpwm_actuator.set_frequency(2000)


if __name__ == "__main__":
    unittest.main()
