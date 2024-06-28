"""RS-485 module"""

from typing import Union
import logging
import struct
from pydantic import BaseModel
from pymodbus.framer import ModbusAsciiFramer, ModbusRtuFramer
from pymodbus.pdu import ModbusResponse
from pymodbus.exceptions import ModbusException
from pymodbus.client import AsyncModbusSerialClient

from .. import get_logger


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


def modbus_config(
    con_params: Union[SerialConnectionConfig, ModbusSerialConnectionConfig]
) -> dict:
    """Build params for pymodbus connection from configuration"""
    modbus_cfg: ModbusSerialConnectionConfig = ModbusSerialConnectionConfig(
        **con_params.model_dump()
    )
    rs485_config: dict = modbus_cfg.model_dump()
    if rs485_config["framer"] == "RTU":
        rs485_config["framer"] = ModbusRtuFramer
    else:
        rs485_config["framer"] = ModbusAsciiFramer
    return rs485_config


async def modbus_read_registers(
    con_params: Union[SerialConnectionConfig, ModbusSerialConnectionConfig],
    start_register: int = 0,
    count: int = 1,
    slave: int = 1,
    logger: Union[logging.Logger, None] = None,
) -> Union[ModbusResponse, None]:
    """Read registers data"""
    response: Union[ModbusResponse, None] = None
    client = AsyncModbusSerialClient(**modbus_config(con_params))
    await client.connect()
    try:
        response = await client.read_holding_registers(
            start_register, count, slave=slave
        )
    except ModbusException as e:
        if logger:
            logger.error("Modbus Exception on read registers %s", e)
    client.close()
    return response


async def modbus_write_register(
    con_params: Union[SerialConnectionConfig, ModbusSerialConnectionConfig],
    register: int,
    value: int,
    slave: int = 1,
    logger: Union[logging.Logger, None] = None,
) -> Union[ModbusResponse, None]:
    """Write data value to the register"""
    response: Union[ModbusResponse, None] = None
    client = AsyncModbusSerialClient(**modbus_config(con_params))
    await client.connect()
    try:
        response = await client.write_register(register, value, slave=slave)
    except ModbusException as e:
        if logger:
            logger.error("Modbus Exception on write register %s", e)
    client.close()
    return response


class RS485Client:
    """RS-485 Client class"""

    def __init__(
        self,
        con_params: Union[SerialConnectionConfig, ModbusSerialConnectionConfig],
        address: int = 1,
        retries: int = 5,
        label: str = "RS485 Device",
        **kwargs,
    ):
        self.con_params: Union[SerialConnectionConfig, ModbusSerialConnectionConfig] = (
            con_params
        )
        self.address: int = address
        self.retries: int = retries
        self.response_delay: float = 5e-3
        self.label: str = label
        self.logger = get_logger(
            self.label, int(kwargs.pop("log_level")) if "log_level" in kwargs else None
        )

    def _parse_response(self, response: bytes) -> dict:
        """Response parser"""
        self.logger.debug("Parsing response: %s", response)
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
            self.logger.debug("Empty response")
            return parsed
        parsed["crc"] = response[-1]
        parsed["addr"] = response[0]
        parsed["cmd"] = response[1]
        if parsed["cmd"] == 3:
            parsed["data_length"] = response[2]
            parsed["count"] = int(parsed["data_length"] / 2)
            parsed["data"] = struct.unpack(">" + "h" * parsed["count"], response[3:-1])
            self.logger.debug(
                "CMD: %s, ADDR: %s, LEN: %s, DATA: %d, CRC: %s",
                parsed["cmd"],
                parsed["addr"],
                parsed["count"],
                parsed["data"],
                parsed["crc"],
            )
        elif parsed["cmd"] == 6:
            parsed["data_length"] = 2
            parsed["count"] = 1
            parsed["register"] = struct.unpack(
                ">" + "h" * parsed["count"], response[2:4]
            )[0]
            parsed["data"] = struct.unpack(">" + "h" * parsed["count"], response[4:6])
            self.logger.debug(
                "CMD: %s, ADDR: %s, REG: %s, DATA: %s, CRC: %s",
                parsed["cmd"],
                parsed["addr"],
                parsed["register"],
                parsed["data"],
                parsed["crc"],
            )
        elif parsed["cmd"] >= 0x80:
            # Error response
            parsed["data_length"] = 2
            parsed["count"] = 1
            parsed["data"] = struct.unpack(">h", response[2:4])
            self.logger.debug(
                "ERR: %x, CMD: %x, DATA: %s, CRC: %s",
                parsed["cmd"],
                parsed["cmd"] - 0x80,
                parsed["data"],
                parsed["crc"],
            )
        return parsed

    def _get_payload(self, response: Union[ModbusResponse, None]) -> bytes:
        """Get the payload from the response"""
        if response:
            if not response.isError():
                # skip start and stop bytes and parse as a hex string
                payload = (
                    struct.pack(">BB", response.slave_id, response.function_code)
                    + response.encode()
                    + b"\x00"
                )
                return payload
            self.logger.debug("Modbus Response Error %s", response.function_code)
        return b""

    async def read_registers(self, start_register: int = 0, count: int = 1) -> bytes:
        """
        Read registers data using pymodbus.
        Redefine this method for serial or custom protocol.
        """
        response: Union[ModbusResponse, None] = await modbus_read_registers(
            self.con_params,
            start_register=start_register,
            count=count,
            slave=self.address,
            logger=self.logger,
        )
        return self._get_payload(response)

    async def write_register(self, register: int, value: int) -> bytes:
        """
        Write the data value to the register using pymodbus.
        Redefine this method for serial or custom protocol.
        """
        response: Union[ModbusResponse, None] = await modbus_write_register(
            self.con_params,
            register=register,
            value=value,
            slave=self.address,
            logger=self.logger,
        )
        return self._get_payload(response)

    async def read_parse_registers(
        self, start_register: int = 0, count: int = 1
    ) -> dict:
        """Read registers and return parsed response"""
        for iteration in range(self.retries):
            self.logger.debug("Iteration %d of %d", iteration + 1, self.retries)
            response = await self.read_registers(
                start_register=start_register, count=count
            )
            parsed = self._parse_response(response)
            if parsed["addr"] == self.address:
                return parsed
        return self._parse_response(b"")

    async def write_parse_register(self, register: int, data: int = 0) -> dict:
        """Write the data value to the register and return parsed response"""
        for iteration in range(self.retries):
            self.logger.debug("Iteration %d of %d", iteration + 1, self.retries)
            response = await self.write_register(register=register, value=data)
            parsed = self._parse_response(response)
            if parsed["addr"] == self.address:
                return parsed
        return self._parse_response(b"")

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
