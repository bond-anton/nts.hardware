"""
Erstevak vacuum gauges. Tested with MTM9D and MTP4D models.
"""

from enum import Enum


class CalibrationFactorPirani(Enum):
    """Calibration coefficients for Pirani gauge (coefficient 1)"""

    AIR = 1.0
    AR = 1.6
    CO = 1.0
    CO2 = 0.89
    H2 = 0.57
    HE = 1.0
    N2 = 1.0
    NE = 1.4
    KR = 2.4


class CalibrationFactorPenning(Enum):
    """Calibration coefficients for Penning gauge (coefficient 2)"""

    AIR = 1.0
    AR = 0.8
    CO2 = 0.74
    H2 = 2.4
    HE = 5.9
    N2 = 1.0
    NE = 3.5
    KR = 0.6
    XE = 0.41


########################################
# Analog output to pressure conversion #
########################################


def voltage_to_pressure(voltage: float, model: str = "MTP4D") -> float:
    """Analog output voltage to pressure (mbar) conversion"""
    if model.strip().upper() in ["MTP4D"]:
        return 10 ** (voltage - 5.5)
    if model.strip().upper() in ["MTM9D"]:
        return 10 ** ((voltage - 6.8) / 0.6)
    return 0.0
