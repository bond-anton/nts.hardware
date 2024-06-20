"""
Erstevak analog output voltage to pressure conversion as well as RS-485 communication protocol.
Tested with MTM9D and MTP4D models.
"""

from typing import Union
import asyncio
from enum import Enum
from decimal import Decimal
from serial import Serial  # type: ignore

from ...rs485 import SerialConnectionConfig


#####################################################
# RS-485 communication                              #
# Erstevak uses nonstandard communication protocol. #
#####################################################


def _checksum(msg: bytes) -> int:
    """Calculate checksum for the message"""
    return sum(list(msg)) % 64 + 64


def _build_message(cmd: str, data: str = "", address=2) -> bytes:
    """Prepare RS-485 message"""
    addr: bytes = f"{address:03d}".encode(encoding="utf-8", errors="strict")
    payload: bytes = str(data).encode(encoding="utf-8", errors="strict")
    if len(payload) > 6:
        raise ValueError("Data can not exceed 6 bytes")
    if cmd not in ("T", "M", "S", "s", "C", "c", "j", "I", "i", "W", "w"):
        raise ValueError("Wrong command")
    cmd_b: bytes = cmd.encode(encoding="utf-8", errors="strict")
    msg = addr + cmd_b + payload
    cs: bytes = chr(_checksum(msg)).encode(encoding="utf-8", errors="strict")
    return msg + cs + "\r".encode(encoding="utf-8", errors="strict")


def f_exp(number):
    """Get exponent of a number"""
    (_, digits, exponent) = Decimal(number).as_tuple()
    return len(digits) + exponent - 1


def f_man(number):
    """Get mantissa of a number"""
    return Decimal(number).scaleb(-f_exp(number)).normalize()


def _pressure_to_data(pressure: float) -> str:
    """Convert pressure (in mbar) to data string"""
    base = int(f_man(pressure) * 1000)
    exp = int(f_exp(pressure) + 20)
    return f"{base:04d}{exp}"


def _parse_pressure(data: str) -> float:
    """Parse pressure (in mbar) from response data"""
    try:
        base: int = int(data[:4])
        exp: int = int(data[-2:]) - 23
        return float(base * 10**exp)
    except TypeError:
        return 0.0


def _calibration_to_data(cal: float) -> str:
    return f"{int(round(cal * 100)):06d}"


def _parse_calibration(data: str) -> float:
    try:
        cal: float = int(data) / 100
        return cal
    except TypeError:
        return 0.0


def _parse_response(resp: bytes, address: int = 2, verbose: bool = True) -> dict:
    """Parse gauge response"""
    # pylint: disable=too-many-branches

    result: dict = {
        "address": None,
        "cmd": None,
        "data": None,
        "cs": None,
        "pressure": None,
        "setpoint": None,
        "calibration": None,
        "gauge_model": None,
        "penning_enabled": None,
        "penning_sync": None,
    }
    if verbose:
        print(f"Parsing response {resp!r}")
    if resp:
        cs: int = _checksum(resp[:-1])
        if verbose:
            print(f"CS calc: {cs!r}, CS: {resp[-1]!r}")
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
                    p = _parse_pressure(result["data"])
                    result["pressure"] = p
                elif result["cmd"] in ("S", "s"):
                    if len(result["data"]) > 1:
                        p = _parse_pressure(result["data"])
                        result["setpoint"] = p
                elif result["cmd"] in ("C", "c"):
                    if len(result["data"]) > 1:
                        cal = _parse_calibration(result["data"])
                        result["calibration"] = cal
                elif result["cmd"] == "j":
                    if len(result["data"]) > 1:
                        p = _parse_pressure(result["data"])
                        result["pressure"] = p
                elif result["cmd"] in ("I", "i"):
                    result["penning_enabled"] = bool(int(result["data"]))
                elif result["cmd"] in ("W", "w"):
                    result["penning_sync"] = bool(int(result["data"]))
            else:
                if verbose:
                    print("Wrong address")
                return result
        else:
            if verbose:
                print("Wrong checksum")
            return result
    return result


class ErstevakRS485:
    """Erstevak gauge RS-485 communication"""

    def __init__(
        self,
        con_params: SerialConnectionConfig,
        address: int = 1,
        retries: int = 5,
        verbose=False,
    ):
        self.con_params: SerialConnectionConfig = con_params
        self.address: int = address
        self.retries = retries
        self.response_delay: float = 5e-3
        self.verbose: bool = verbose

    async def send_command(self, command: str, data: str = "") -> dict:
        """Send command request to the gauge and receive a response"""
        connection: Serial
        parsed_data: dict
        response: bytes = b""
        for iteration in range(self.retries):
            if self.verbose:
                print(f"Iteration {iteration + 1} of {self.retries}")
            msg: bytes = _build_message(command, data, self.address)
            if self.verbose:
                print(f"MSG: {msg!r}")
            connection = Serial(**self.con_params.model_dump())
            connection.write(msg)
            await asyncio.sleep(self.response_delay)
            response = connection.readline()[:-1]
            connection.close()
            parsed_data = _parse_response(response, self.address, verbose=self.verbose)
            if parsed_data["cmd"] == command:
                return parsed_data
        return _parse_response(response, self.address, verbose=self.verbose)

    async def get_gauge_type(self) -> str:
        """Get gauge model"""
        data = await self.send_command("T")
        if data["cmd"] == "T":
            return data["gauge_model"]
        return ""

    async def get_pressure(self) -> float:
        """Get pressure measurement"""
        data = await self.send_command("M")
        if data["cmd"] == "M":
            return data["pressure"]
        return 0.0

    async def get_setpoint(self, sp: int = 1) -> float:
        """Get setpoint pressure"""
        data = await self.send_command("S", f"{sp}")
        if data["cmd"] == "S":
            return data["setpoint"]
        return 0.0

    async def set_setpoint(self, pressure: float, sp: int = 1) -> float:
        """Set setpoint pressure"""
        # unlock setpoint register
        data = await self.send_command("s", f"{sp}")
        if data["cmd"] == "s":
            if data["data"] == f"{sp}":  # unlocked
                # write setpoint value to register
                data = await self.send_command("s", _pressure_to_data(pressure))
                if data["cmd"] == "s" and data["setpoint"]:
                    return data["setpoint"]
        # if failed try to read setpoint value from register
        return await self.get_setpoint(sp)

    async def get_calibration(self, cal_n: int = 1) -> float:
        """Get calibration coefficient"""
        data = await self.send_command("C", f"{cal_n}")
        if data["cmd"] == "C":
            return data["calibration"]
        return 0.0

    async def set_calibration(self, cal: Union[float, Enum], cal_n: int = 1) -> float:
        """Set calibration coefficient"""
        # unlock calibration register
        data = await self.send_command("c", f"{cal_n}")
        if data["cmd"] == "c":
            if data["data"] == f"{cal_n}":  # unlocked
                # write calibration value to register
                if isinstance(cal, Enum):
                    cal_f = cal.value
                else:
                    cal_f = float(cal)
                data = await self.send_command("c", _calibration_to_data(cal_f))
                if data["cmd"] == "c" and data["calibration"]:
                    return data["calibration"]
        # if failed try to read calibration value from register
        return await self.get_calibration(cal_n)

    async def set_atmosphere(self) -> float:
        """Calibrate atmospheric pressure"""
        # unlock register
        data = await self.send_command("j", "1")
        if data["cmd"] == "j":
            if data["data"] == "1":  # unlocked
                # write value to register
                data = await self.send_command("j", "100023")
                if data["cmd"] == "j" and data["pressure"]:
                    return data["pressure"]
        return 0.0

    async def set_zero(self) -> float:
        """Calibrate zero pressure"""
        # unlock register
        data = await self.send_command("j", "0")
        if data["cmd"] == "j":
            if data["data"] == "0":  # unlocked
                # write value to register
                data = await self.send_command("j", "000000")
                if data["cmd"] == "j" and data["pressure"]:
                    return data["pressure"]
        return 0.0

    async def get_penning_state(self) -> bool:
        """
        Read the ON/OFF state of the penning gauge.
        Return True if penning is ON, False otherwise.
        """
        data = await self.send_command("I")
        if data["cmd"] == "I" and data["penning_enabled"] is not None:
            return data["penning_enabled"]
        return False

    async def set_penning_state(self, enable: bool = True) -> float:
        """Set penning gauge to ON/OFF"""
        data = await self.send_command("i", f"{int(enable)}")
        if data["cmd"] == "i" and data["penning_enabled"] is not None:
            return data["penning_enabled"]
        return await self.get_penning_state()

    async def get_penning_sync(self) -> bool:
        """
        Read the ON/OFF state of the penning-pirani synchronization.
        Return True if sync is ON, False otherwise.
        """
        data = await self.send_command("W")
        if data["cmd"] == "W" and data["penning_sync"] is not None:
            return data["penning_sync"]
        return False

    async def set_penning_sync(self, enable: bool = True) -> float:
        """Set penning-pirani sync to ON/OFF"""
        data = await self.send_command("w", f"{int(enable):06d}")
        if data["cmd"] == "w" and data["penning_sync"] is not None:
            return data["penning_sync"]
        return await self.get_penning_sync()
