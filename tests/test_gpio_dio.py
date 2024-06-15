""" Testing GPIO digital input and output """

import unittest

from gpiozero import OutputDevice, DigitalInputDevice  # type: ignore

try:
    from src.nts.hardware.gpio import RelayConfig, ButtonConfig, get_relay, get_button
except ModuleNotFoundError:
    from nts.hardware.gpio import RelayConfig, ButtonConfig, get_relay, get_button


class TestGpio(unittest.TestCase):
    """
    Test GPIO Output device functionality.
    """

    def test_relay_config(self) -> None:
        """Test RelayConfig class"""
        rl_cfg = RelayConfig(pin_number=1)
        self.assertEqual(rl_cfg.label, "Relay")
        self.assertEqual(rl_cfg.backend, "gpiozero")
        self.assertEqual(rl_cfg.pin_number, 1)
        rl_cfg.pin_number = 3
        self.assertEqual(rl_cfg.pin_number, 3)
        self.assertTrue(rl_cfg.emulation)
        self.assertTrue(rl_cfg.active_high)
        self.assertFalse(rl_cfg.initial_value)

    def test_get_relay(self) -> None:
        """Test get_relay function"""
        rl_cfg = RelayConfig(pin_number=1)
        relay = get_relay(rl_cfg)
        self.assertIsInstance(relay, OutputDevice)
        rl_cfg = RelayConfig(pin_number=3, backend="gpiod")
        with self.assertRaises(NotImplementedError):
            get_relay(rl_cfg)
        rl_cfg = RelayConfig(pin_number=3, backend="some_backend")
        with self.assertRaises(NotImplementedError):
            get_relay(rl_cfg)

    def test_button_config(self) -> None:
        """Test ButtonConfig class"""
        btn_cfg = ButtonConfig(pin_number=1)
        self.assertEqual(btn_cfg.label, "Button")
        self.assertEqual(btn_cfg.backend, "gpiozero")
        self.assertEqual(btn_cfg.pin_number, 1)
        btn_cfg.pin_number = 3
        self.assertEqual(btn_cfg.pin_number, 3)
        self.assertTrue(btn_cfg.emulation)
        self.assertTrue(btn_cfg.pull_up)
        self.assertEqual(btn_cfg.bounce_time, 0.0)

    def test_get_button(self) -> None:
        """Test get_button function"""
        btn_cfg = ButtonConfig(pin_number=1)
        button = get_button(btn_cfg)
        self.assertIsInstance(button, DigitalInputDevice)
        btn_cfg = ButtonConfig(pin_number=3, backend="gpiod")
        with self.assertRaises(NotImplementedError):
            get_button(btn_cfg)
        btn_cfg = ButtonConfig(pin_number=3, backend="some_backend")
        with self.assertRaises(NotImplementedError):
            get_button(btn_cfg)
