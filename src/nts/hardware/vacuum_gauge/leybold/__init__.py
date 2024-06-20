"""
Leybold analog output voltage to pressure conversion.
"""

from enum import Enum


class CalibrationFactorPirani(Enum):
    """Calibration coefficients for Pirani gauge (coefficient 1)"""

    AIR = 1.0  # Valid in the range 3e-3 to 3e-1 mbar
    AR = 1.57  # Valid in the range 3e-3 to 1e+0 mbar
    CO = 1.0  # Valid in the range 3e-3 to 3e-1 mbar
    H2 = 0.84  # Valid in the range 3e-3 to 2e-1 mbar
    HE = 1.4  # Valid in the range 3e-3 to 3e-1 mbar
    N2 = 1.0  # Valid in the range 3e-3 to 3e-1 mbar
    O2 = 1.0  # Valid in the range 3e-3 to 3e-1 mbar


########################################
# Analog output to pressure conversion #
########################################


def voltage_to_pressure(voltage: float, model: str = "Leybold") -> float:
    """Analog output voltage to pressure (mbar) conversion"""
    if model.strip().upper() in ["TTR 101 N THERMOVAC", "TTR 101 N", "TTR101N"]:
        if voltage < 0.6119:
            return 5e-5
        if voltage > 10.2275:
            return 1.5e3
        return 10 ** ((voltage - 6.143) / 1.286)
    return 0.0
