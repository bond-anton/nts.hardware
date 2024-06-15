""" Testing GPIO PWM """

import unittest

from gpiozero import PWMOutputDevice  # type: ignore

try:
    from src.nts.hardware.gpio import PWMConfig, get_pwm
except ModuleNotFoundError:
    from nts.hardware.gpio import PWMConfig, get_pwm


class TestGpioPWM(unittest.TestCase):
    """
    Test GPIO PWM device functionality.
    """

    def test_pwm_config(self) -> None:
        """Test PWMConfig class"""
        pwm_cfg = PWMConfig(pin_number=1)
        self.assertEqual(pwm_cfg.label, "PWM")
        self.assertEqual(pwm_cfg.backend, "gpiozero")
        self.assertEqual(pwm_cfg.pin_number, 1)
        pwm_cfg.pin_number = 3
        self.assertEqual(pwm_cfg.pin_number, 3)
        self.assertTrue(pwm_cfg.emulation)
        self.assertTrue(pwm_cfg.active_high)
        self.assertEqual(pwm_cfg.initial_value, 0.0)

    def test_get_pwm(self) -> None:
        """Test get_pwm function"""
        pwm_cfg = PWMConfig(pin_number=1)
        pwm = get_pwm(pwm_cfg)
        self.assertIsInstance(pwm, PWMOutputDevice)
        pwm_cfg = PWMConfig(
            channel=0, chip=0, frequency=5000, backend="rpi_hardware_pwm"
        )
        pwm = get_pwm(pwm_cfg)
        self.assertEqual(pwm.pwm_channel, pwm_cfg.channel)
        pwm_cfg = PWMConfig(pin_number=3, backend="gpiod")
        with self.assertRaises(NotImplementedError):
            get_pwm(pwm_cfg)
        pwm_cfg = PWMConfig(pin_number=3, backend="some_backend")
        with self.assertRaises(NotImplementedError):
            get_pwm(pwm_cfg)
