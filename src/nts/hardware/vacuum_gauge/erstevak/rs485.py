"""
Erstevak analog output voltage to pressure conversion as well as RS-485 communication protocol.
Tested with MTM9D and MTP4D models.
"""

from typing import Union
import asyncio
from enum import Enum
from decimal import Decimal
from serial import Serial  # type: ignore

from ...rs485 import SerialConnectionConfig, RS485Client


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


def _pressure_to_data(pressure: float) -> int:
    """Convert pressure (in mbar) to data string"""
    base = int(f_man(pressure) * 1000)
    exp = int(f_exp(pressure) + 20)
    return int(f"{base:04d}{exp}")


def _parse_pressure(data: str) -> float:
    """Parse pressure (in mbar) from response data"""
    try:
        base: int = int(data[:4])
        exp: int = int(data[-2:]) - 23
        return float(base * 10**exp)
    except TypeError:
        return 0.0


def _calibration_to_data(cal: float) -> int:
    return int(round(cal * 100))


def _parse_calibration(data: str) -> float:
    try:
        cal: float = int(data) / 100
        return cal
    except TypeError:
        return 0.0


class ErstevakRS485(RS485Client):
    """Erstevak gauge RS-485 communication"""

    def __init__(
        self,
        con_params: SerialConnectionConfig,
        address: int = 1,
        retries: int = 5,
        label: str = "Erstevak Gauge",
        **kwargs,
    ):
        # pylint: disable=R0801
        super().__init__(
            SerialConnectionConfig(**con_params.model_dump()),
            address,
            retries,
            label,
            **kwargs,
        )
        self._registers: dict[int, str] = {
            0: "T",
            1: "M",
            2: "S",
            3: "s",
            4: "s",
            5: "C",
            6: "c",
            7: "c",
            8: "j",
            9: "j",
            10: "I",
            11: "i",
            12: "W",
            13: "w",
        }

    def _parse_response(self, response: bytes) -> dict:
        """Parse gauge response"""
        # pylint: disable=too-many-branches

        result: dict = {
            "addr": None,
            "cmd": None,
            "data": None,
            "crc": None,
            "pressure": None,
            "setpoint": None,
            "calibration": None,
            "gauge_model": None,
            "penning_enabled": None,
            "penning_sync": None,
        }
        self.logger.debug("Parsing response %s", response)
        if response:
            cs: int = _checksum(response[:-1])
            self.logger.debug("CS calc: %s, CS: %s", cs, response[-1])
            if cs == response[-1]:
                response_data: str = response.decode()[:-1]
                r_address: int = int(response_data[:3])
                if self.address == r_address:
                    result["addr"] = self.address
                    result["cmd"] = response_data[3]
                    result["data"] = response_data[4:]
                    result["crc"] = cs
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
                    self.logger.error("Wrong address")
                    return result
            else:
                self.logger.error("Wrong checksum")
                return result
        return result

    async def read_registers(self, start_register: int = 0, count: int = 1) -> bytes:
        """Send command to gauge and read data"""
        con: Serial
        if start_register not in (0, 1, 10, 12):
            return b""
        command = self._registers[start_register]
        msg: bytes = _build_message(command, "", self.address)
        self.logger.debug("RS485 MSG: %s", msg)
        con = Serial(**self.con_params.model_dump())
        con.write(msg)
        await asyncio.sleep(self.response_delay)
        response: bytes = con.read_until(b"\r")[:-1]
        con.close()
        return response

    async def write_register(self, register: int, value: int) -> bytes:
        """Write the data value to the register"""
        con: Serial
        data: str
        if register in (0, 1, 10, 12):
            return b""
        command = self._registers[register]
        if register in (4, 7, 9, 13):
            data = f"{int(value):06d}"
        else:
            data = f"{int(value)}"
        msg: bytes = _build_message(command, data, self.address)
        self.logger.debug("RS485 MSG: %s", msg)
        con = Serial(**self.con_params.model_dump())
        con.write(msg)
        await asyncio.sleep(self.response_delay)
        response: bytes = con.read_until(b"\r")[:-1]
        con.close()
        return response

    async def get_gauge_type(self) -> str:
        """Get gauge model"""
        data = await self.read_parse_registers(0)
        if data["cmd"] == "T":
            return data["gauge_model"]
        return ""

    async def get_pressure(self) -> float:
        """Get pressure measurement"""
        data = await self.read_parse_registers(1)
        if data["cmd"] == "M":
            return data["pressure"]
        return 0.0

    async def get_setpoint(self, sp: int = 1) -> float:
        """Get setpoint pressure"""
        data = await self.write_parse_register(2, sp)
        if data["cmd"] == "S":
            return data["setpoint"]
        return 0.0

    async def set_setpoint(self, pressure: float, sp: int = 1) -> float:
        """Set setpoint pressure"""
        # unlock setpoint register
        data = await self.write_parse_register(3, sp)
        if data["cmd"] == "s":
            if data["data"] == f"{sp}":  # unlocked
                # write setpoint value to register
                data = await self.write_parse_register(4, _pressure_to_data(pressure))
                if data["cmd"] == "s" and data["setpoint"]:
                    return data["setpoint"]
        # if failed try to read setpoint value from register
        return await self.get_setpoint(sp)

    async def get_calibration(self, cal_n: int = 1) -> float:
        """Get calibration coefficient"""
        data = await self.write_parse_register(5, cal_n)
        if data["cmd"] == "C":
            return data["calibration"]
        return 0.0

    async def set_calibration(self, cal: Union[float, Enum], cal_n: int = 1) -> float:
        """Set calibration coefficient"""
        # unlock calibration register
        data = await self.write_parse_register(6, cal_n)
        if data["cmd"] == "c":
            if data["data"] == f"{cal_n}":  # unlocked
                # write calibration value to register
                if isinstance(cal, Enum):
                    cal_f = cal.value
                else:
                    cal_f = float(cal)
                data = await self.write_parse_register(7, _calibration_to_data(cal_f))
                if data["cmd"] == "c" and data["calibration"]:
                    return data["calibration"]
        # if failed try to read calibration value from register
        return await self.get_calibration(cal_n)

    async def set_atmosphere(self) -> float:
        """Calibrate atmospheric pressure"""
        # unlock register
        data = await self.write_parse_register(8, 1)
        if data["cmd"] == "j":
            if data["data"] == "1":  # unlocked
                # write value to register
                data = await self.write_parse_register(9, _pressure_to_data(1000.0))
                if data["cmd"] == "j" and data["pressure"]:
                    return data["pressure"]
        return 0.0

    async def set_zero(self) -> float:
        """Calibrate zero pressure"""
        # unlock register
        data = await self.write_parse_register(8, 0)
        if data["cmd"] == "j":
            if data["data"] == "0":  # unlocked
                # write value to register
                data = await self.write_parse_register(9, 0)
                if data["cmd"] == "j" and data["pressure"]:
                    return data["pressure"]
        return 0.0

    async def get_penning_state(self) -> bool:
        """
        Read the ON/OFF state of the penning gauge.
        Return True if penning is ON, False otherwise.
        """
        data = await self.read_parse_registers(7)
        if data["cmd"] == "I" and data["penning_enabled"] is not None:
            return data["penning_enabled"]
        return False

    async def set_penning_state(self, enable: bool = True) -> float:
        """Set penning gauge to ON/OFF"""
        data = await self.write_parse_register(11, int(bool(enable)))
        if data["cmd"] == "i" and data["penning_enabled"] is not None:
            return data["penning_enabled"]
        return await self.get_penning_state()

    async def get_penning_sync(self) -> bool:
        """
        Read the ON/OFF state of the penning-pirani synchronization.
        Return True if sync is ON, False otherwise.
        """
        data = await self.read_parse_registers(9)
        if data["cmd"] == "W" and data["penning_sync"] is not None:
            return data["penning_sync"]
        return False

    async def set_penning_sync(self, enable: bool = True) -> float:
        """Set penning-pirani sync to ON/OFF"""
        data = await self.write_parse_register(13, int(bool(enable)))
        if data["cmd"] == "w" and data["penning_sync"] is not None:
            return data["penning_sync"]
        return await self.get_penning_sync()
