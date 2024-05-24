"""
Erstevak analog output voltage to pressure conversion as well as RS-485 communication protocol.
Tested with MTM9D and MTP4D models.
"""

from typing import Union
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


########################
# RS-485 communication #
########################


def checksum(msg: bytes) -> bytes:
    """Calculate checksum for the message"""
    return chr(sum(list(msg)) % 64 + 64).encode(encoding="utf-8", errors="strict")


def build_message(cmd: str, data: str = "", address=2) -> bytes:
    """Prepare RS-485 message"""
    addr: bytes = f"{address:03d}".encode(encoding="utf-8", errors="strict")
    payload: bytes = str(data).encode(encoding="utf-8", errors="strict")
    if len(payload) > 6:
        raise ValueError("Data can not exceed 6 bytes")
    if cmd not in ("T", "M", "S", "s", "C", "c", "j"):
        raise ValueError("Wrong command")
    cmd_b: bytes = cmd.encode(encoding="utf-8", errors="strict")
    msg = addr + cmd_b + payload
    cs: bytes = checksum(msg)
    return msg + cs + "\r".encode(encoding="utf-8", errors="strict")


def parse_response(
    resp: bytes, address: int = 2, verbose: bool = True
) -> Union[dict, None]:
    """Parse gauge response"""

    result: dict = {
        "address": None,
        "cmd": None,
        "data": None,
        "cs": None,
        "pressure": None,
        "gauge_model": None,
    }

    if resp:
        cs: bytes = checksum(resp[:-1])
        if cs == resp[-1]:
            response: str = resp.decode()[:-1]
            r_address: int = int(response[:3])
            if address == r_address:
                result["address"] = address
                result["cmd"] = response[3]
                result["data"] = response[4:]
                result["cs"] = cs
                if result["cmd"] == "T":
                    result["gauge_model"] = result["data"]
                elif result["cmd"] == "M":
                    p = parse_pressure(result["data"])
                    result["pressure"] = p
            else:
                return None
        else:
            if verbose:
                print("Wrong checksum")
            return None
    return result


def parse_pressure(data: str) -> float:
    """Parse pressure (in mbar) from response data"""
    try:
        base: int = int(data[:4])
        exp: int = int(data[-2:]) - 23
        return float(base * 10**exp)
    except TypeError:
        return 0.0


def gauge_type_request(address: int = 2) -> bytes:
    """Build gauge type request command"""
    return build_message("T", address=address)


def measurement_request(address: int = 2) -> bytes:
    """Build measurement data request command"""
    return build_message("M", address=address)


def send_request(con: Serial, request: bytes) -> None:
    """Write request to serial communication bus"""
    con.write(request)


def get_response(con: Serial) -> bytes:
    """Read data from serial communication bus"""
    return con.readline()[:-1]
