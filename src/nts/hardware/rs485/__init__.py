"""RS-485 module"""

from typing import Union
import struct
from pydantic import BaseModel


class SerialConnectionConfig(BaseModel):
    """Model for serial communication configuration"""

    port: str = "/dev/serial0"  # port is a device name e.g. /dev/ttyUSB0 or COM3
    baudrate: int = 9600
    bytesize: int = 8
    parity: str = "N"
    stopbits: int = 1
    timeout: Union[float, None] = None  # read timeout in seconds (float)
    write_timeout: Union[float, None] = None  # write timeout in seconds (float)
    inter_byte_timeout: Union[float, None] = (
        None  # Inter-character timeout, None to disable
    )


class ModbusSerialConnectionConfig(BaseModel):
    """Model for modbus serial communication configuration"""

    framer: str = "RTU"
    port: str = "/dev/serial0"  # port is a device name e.g. /dev/ttyUSB0 or COM3
    baudrate: int = 9600
    bytesize: int = 8
    parity: str = "N"
    stopbits: int = 1


class RS485Client:
    """RS-485 Client class"""

    def __init__(
        self,
        con_params: Union[SerialConnectionConfig, ModbusSerialConnectionConfig],
        address: int = 1,
        retries: int = 5,
        verbose=False,
    ):
        self.con_params: Union[SerialConnectionConfig, ModbusSerialConnectionConfig] = (
            con_params
        )
        self.address: int = address
        self.retries: int = retries
        self.response_delay: float = 5e-3
        self.verbose: bool = verbose

    @staticmethod
    def _parse_response(response: bytes, verbose: bool = True) -> dict:
        """Response parser"""
        if verbose:
            print(f"Parsing response: {response!r}")
        parsed: dict = {
            "crc": 0,
            "addr": -1,  # 0 is reserved for MODBUS as a broadcast address
            "cmd": 0,
            "data_length": 0,
            "register": 0,
            "count": 0,
            "data": tuple(),
        }
        if not response:
            if verbose:
                print("Empty response")
            return parsed
        parsed["crc"] = response[-1]
        parsed["addr"] = response[0]
        parsed["cmd"] = response[1]
        if parsed["cmd"] == 3:
            parsed["data_length"] = response[2]
            parsed["count"] = int(parsed["data_length"] / 2)
            parsed["data"] = struct.unpack(">" + "h" * parsed["count"], response[3:-1])
            if verbose:
                print(
                    f"CMD: {parsed['cmd']}, ADDR: {parsed['addr']}, LEN: {parsed['count']}, "
                    f"DATA: {parsed['data']}, CRC: {parsed['crc']}"
                )
        elif parsed["cmd"] == 6:
            parsed["data_length"] = 2
            parsed["count"] = 1
            parsed["register"] = struct.unpack(
                ">" + "h" * parsed["count"], response[2:4]
            )[0]
            parsed["data"] = struct.unpack(">" + "h" * parsed["count"], response[4:6])
            if verbose:
                print(
                    f"CMD: {parsed['cmd']}, ADDR: {parsed['addr']}, REG: {parsed['register']}, "
                    f"DATA: {parsed['data']}, CRC: {parsed['crc']}"
                )
        elif parsed["cmd"] >= 0x80:
            # Error response
            parsed["data_length"] = 2
            parsed["count"] = 1
            parsed["data"] = struct.unpack(">h", response[2:4])
            if verbose:
                print(
                    f"ERR: {parsed['cmd']:x}, CMD: {parsed['cmd'] - 0x80}"
                    f"DATA: {parsed['data']}, CRC: {parsed['crc']}"
                )
        return parsed

    async def read_registers(self, start_register: int = 0, count: int = 1) -> bytes:
        """Read multiple registers data"""
        # replace this method with actual communication action
        if self.verbose:
            print(f"Read from REGs: {start_register} - {start_register + count}")
        return b""

    async def read_parse_registers(
        self, start_register: int = 0, count: int = 1
    ) -> dict:
        """Read registers and return parsed response"""
        for iteration in range(self.retries):
            if self.verbose:
                print(f"Iteration {iteration + 1} of {self.retries}")
            response = await self.read_registers(
                start_register=start_register, count=count
            )
            parsed = self._parse_response(response, verbose=self.verbose)
            if parsed["addr"] == self.address:
                return parsed
        return self._parse_response(b"", verbose=self.verbose)

    async def write_register(self, register: int, value: int) -> bytes:
        """Write the data value to the register"""
        # replace this method with actual communication action
        if self.verbose:
            print(f"Write to REG: {register}, VAL: {value}")
        return b""

    async def write_parse_register(self, register: int, data: int = 0) -> dict:
        """Write the data value to the register and return parsed response"""
        for iteration in range(self.retries):
            if self.verbose:
                print(f"Iteration {iteration + 1} of {self.retries}")
            response = await self.write_register(register=register, value=data)
            parsed = self._parse_response(response, verbose=self.verbose)
            if parsed["addr"] == self.address:
                return parsed
        return self._parse_response(b"", verbose=self.verbose)

    async def read_single_register_float(
        self, register: int, factor: int = 100
    ) -> float:
        """Parse a float number from the register data value divided by provided factor"""
        response: dict = await self.read_parse_registers(register, 1)
        if response["data"]:
            return float(response["data"][0] / factor)
        return 0.0

    async def write_single_register_float(
        self, register: int, value: float, factor: int = 100
    ) -> float:
        """Write a float number to the register multiplied by the provided factor"""
        response = await self.write_parse_register(register, int(round(value * factor)))
        if response["cmd"] == 6 and response["data"]:
            return float(response["data"][0] / factor)
        return await self.read_single_register_float(register, factor)

    async def read_two_registers_data(
        self, start_register: int, factor: int = 100
    ) -> float:
        """Parse a float number from the data split between two registers"""
        response: dict = await self.read_parse_registers(start_register, 2)
        if response["data"]:
            return float(((response["data"][0] << 16) + response["data"][1]) / factor)
        return 0.0
