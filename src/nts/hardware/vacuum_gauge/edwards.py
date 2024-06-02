"""
Edwards analog output voltage to pressure conversion.
"""

########################################
# Analog output to pressure conversion #
########################################


def voltage_to_pressure(voltage: float, model: str = "Edwards") -> float:
    """Analog output voltage to pressure (mbar) conversion"""
    if model.strip().upper() in ["Edwards"]:
        return 10 ** (voltage - 5.555)
    return 0.0
