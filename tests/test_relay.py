""" Testing Relay class """

import unittest

try:
    from src.nts.hardware.relay import Relay
except ModuleNotFoundError:
    from nts.hardware.relay import Relay


class TestRelay(unittest.TestCase):
    """
    Test Relay class.
    """

    def test_constructor(self) -> None:
        """
        test Relay constructor.
        """
        # pylint: disable=protected-access
        relay = Relay()
        self.assertEqual(relay.label, "RELAY")
        self.assertEqual(relay._is_normally_off(), True)
        self.assertEqual(relay.normally_off, True)
        self.assertEqual(relay.normally_on, False)
        self.assertEqual(relay.value, 0)
        self.assertEqual(relay.verbose, False)

        relay = Relay(label="MY RELAY", normally_off=False, verbose=True)
        self.assertEqual(relay.label, "MY RELAY")
        self.assertEqual(relay._is_normally_off(), False)
        self.assertEqual(relay.normally_off, False)
        self.assertEqual(relay.normally_on, True)
        self.assertEqual(relay.value, 1)
        self.assertEqual(relay.verbose, True)

        relay = Relay(label="MY RELAY", normally_on=True, verbose=False)
        self.assertEqual(relay.label, "MY RELAY")
        self.assertEqual(relay._is_normally_off(), False)
        self.assertEqual(relay.normally_off, False)
        self.assertEqual(relay.normally_on, True)
        self.assertEqual(relay.value, 1)
        self.assertEqual(relay.verbose, False)

        relay = Relay(label="MY RELAY", normally_on=False, verbose=True)
        self.assertEqual(relay.label, "MY RELAY")
        self.assertEqual(relay._is_normally_off(), True)
        self.assertEqual(relay.normally_off, True)
        self.assertEqual(relay.normally_on, False)
        self.assertEqual(relay.value, 0)
        self.assertEqual(relay.verbose, True)

    def test_label(self):
        """Test label property"""
        relay = Relay(label="MY RELAY")
        self.assertEqual(relay.label, "MY RELAY")
        relay.label = "SOME Label"
        self.assertEqual(relay.label, "SOME Label")

    def test_verbose(self):
        """Test verbose property"""
        relay = Relay(label="MY RELAY")
        self.assertEqual(relay.verbose, False)
        relay.verbose = True
        self.assertEqual(relay.verbose, True)
        relay.verbose = False
        self.assertEqual(relay.verbose, False)

    def test_value(self):
        """Test value property"""
        relay = Relay()
        self.assertEqual(relay.value, 0)
        self.assertEqual(relay.current_state, relay.off)
        relay.value = 1
        self.assertEqual(relay.value, 1)
        self.assertEqual(relay.current_state, relay.on)
        relay.value = 0
        self.assertEqual(relay.value, 0)
        self.assertEqual(relay.current_state, relay.off)
        relay.value = 0.5
        self.assertEqual(relay.value, 1)
        self.assertEqual(relay.current_state, relay.on)
        relay.value = 0.1
        self.assertEqual(relay.value, 0)
        self.assertEqual(relay.current_state, relay.off)
        relay.value = 0.6
        self.assertEqual(relay.value, 1)
        self.assertEqual(relay.current_state, relay.on)

    def test_switching(self):
        """Test switching on and off"""
        relay = Relay(verbose=True)
        self.assertEqual(relay.value, 0)
        self.assertEqual(relay.current_state, relay.off)
        relay.switch_on()
        self.assertEqual(relay.value, 1)
        self.assertEqual(relay.current_state, relay.on)
        relay.switch_off()
        self.assertEqual(relay.value, 0)
        self.assertEqual(relay.current_state, relay.off)


if __name__ == "__main__":
    unittest.main()
