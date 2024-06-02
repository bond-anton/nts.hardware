"""
Edwards analog output voltage to pressure conversion.
"""

from serial import Serial  # type: ignore


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
