"""
Edwards analog output voltage to pressure conversion.
"""

########################################
# Analog output to pressure conversion #
########################################


def voltage_to_pressure(voltage: float, model: str = "Leybold") -> float:
    """Analog output voltage to pressure (mbar) conversion"""
    if model.strip().upper() in ["Leybold"]:
        return 10 ** (((voltage + 0.1) * 2 - 6.143) / 1.286)
    return 0.0
