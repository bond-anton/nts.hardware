""" Testing ProportionalActuator class """

import unittest

try:
    from src.nts.hardware.actuator import ProportionalActuator
except ModuleNotFoundError:
    from nts.hardware.actuator import ProportionalActuator


class TestProportionalActuator(unittest.TestCase):
    """
    Test ProportionalActuator class.
    """

    def test_constructor(self) -> None:
        """
        test ProportionalActuator constructor.
        """
        # pylint: disable=protected-access
        actuator = ProportionalActuator()
        self.assertEqual(actuator.label, "ACTUATOR")
        self.assertEqual(actuator._is_normally_off(), True)
        self.assertEqual(actuator.normally_off, True)
        self.assertEqual(actuator.normally_on, False)
        self.assertEqual(actuator.value, 0)
        self.assertEqual(actuator.verbose, False)

        actuator = ProportionalActuator(
            label="MY ACTUATOR", normally_off=False, verbose=True
        )
        self.assertEqual(actuator.label, "MY ACTUATOR")
        self.assertEqual(actuator._is_normally_off(), False)
        self.assertEqual(actuator.normally_off, False)
        self.assertEqual(actuator.normally_on, True)
        self.assertEqual(actuator.value, 1)
        self.assertEqual(actuator.verbose, True)

        actuator = ProportionalActuator(
            label="MY ACTUATOR", normally_on=True, verbose=False
        )
        self.assertEqual(actuator.label, "MY ACTUATOR")
        self.assertEqual(actuator._is_normally_off(), False)
        self.assertEqual(actuator.normally_off, False)
        self.assertEqual(actuator.normally_on, True)
        self.assertEqual(actuator.value, 1)
        self.assertEqual(actuator.verbose, False)

        actuator = ProportionalActuator(
            label="MY ACTUATOR", normally_on=False, verbose=True
        )
        self.assertEqual(actuator.label, "MY ACTUATOR")
        self.assertEqual(actuator._is_normally_off(), True)
        self.assertEqual(actuator.normally_off, True)
        self.assertEqual(actuator.normally_on, False)
        self.assertEqual(actuator.value, 0)
        self.assertEqual(actuator.verbose, True)

    def test_label(self):
        """Test label property"""
        actuator = ProportionalActuator(label="MY ACTUATOR")
        self.assertEqual(actuator.label, "MY ACTUATOR")
        actuator.label = "SOME Label"
        self.assertEqual(actuator.label, "SOME Label")

    def test_verbose(self):
        """Test verbose property"""
        actuator = ProportionalActuator(label="MY ACTUATOR")
        self.assertEqual(actuator.verbose, False)
        actuator.verbose = True
        self.assertEqual(actuator.verbose, True)
        actuator.verbose = False
        self.assertEqual(actuator.verbose, False)

    def test_value(self):
        """Test value property"""
        actuator = ProportionalActuator()
        self.assertEqual(actuator.value, 0)
        self.assertEqual(actuator.current_state, actuator.off)
        actuator.value = 1
        self.assertEqual(actuator.value, 1)
        self.assertEqual(actuator.current_state, actuator.on)
        actuator.value = 0
        self.assertEqual(actuator.value, 0)
        self.assertEqual(actuator.current_state, actuator.off)
        actuator.value = 0.5
        self.assertEqual(actuator.value, 0.5)
        self.assertEqual(actuator.current_state, actuator.on)
        actuator.value = 0.1
        self.assertEqual(actuator.value, 0.1)
        self.assertEqual(actuator.current_state, actuator.on)
        actuator.value = 1.1
        self.assertEqual(actuator.value, 1)
        self.assertEqual(actuator.current_state, actuator.on)
        actuator.value = -1
        self.assertEqual(actuator.value, 0)
        self.assertEqual(actuator.current_state, actuator.off)

    def test_switching(self):
        """Test switching on and off"""
        actuator = ProportionalActuator(verbose=True)
        self.assertEqual(actuator.value, 0)
        self.assertEqual(actuator.current_state, actuator.off)
        actuator.switch_on()
        self.assertEqual(actuator.value, 1)
        self.assertEqual(actuator.current_state, actuator.on)
        actuator.value = 0.1
        self.assertEqual(actuator.value, 0.1)
        self.assertEqual(actuator.current_state, actuator.on)
        actuator.switch_off()
        self.assertEqual(actuator.value, 0)
        self.assertEqual(actuator.current_state, actuator.off)
        actuator.switch_on()
        self.assertEqual(actuator.value, 0.1)
        self.assertEqual(actuator.current_state, actuator.on)


if __name__ == "__main__":
    unittest.main()
