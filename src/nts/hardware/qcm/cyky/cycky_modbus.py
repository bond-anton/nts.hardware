"""Functions to communicate with CYKY thickness monitor TM106B using pymodbus"""

from typing import Union
import struct

from pymodbus.client import AsyncModbusSerialClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ModbusResponse

from .cyky import QTM
from ...rs485 import ModbusSerialConnectionConfig, modbus_config


class QTMModbus(QTM):
    """Quartz crystal thickness monitor"""

    # pylint: disable=too-many-public-methods

    def __init__(
        self,
        con_params: ModbusSerialConnectionConfig,
        address: int = 1,
        retries: int = 5,
        verbose=False,
    ):
        super().__init__(
            ModbusSerialConnectionConfig(**con_params.model_dump()),
            address,
            retries,
            verbose,
        )

    @staticmethod
    def _get_payload(
        response: Union[ModbusResponse, None], verbose: bool = True
    ) -> bytes:
        """Get the payload from the QTM response"""
        if response:
            if not response.isError():
                # skip start and stop bytes and parse as a hex string
                payload = (
                    struct.pack(">BB", response.slave_id, response.function_code)
                    + response.encode()
                    + b"\x00"
                )
                return payload
            if verbose:
                print(f"Modbus Response Error {response.function_code}")
        return b""

    async def read_registers(self, start_register: int = 0, count: int = 1) -> bytes:
        """Read QTM registers data"""
        response: Union[ModbusResponse, None] = None
        client = AsyncModbusSerialClient(**modbus_config(self.con_params))
        await client.connect()
        try:
            response = await client.read_holding_registers(
                start_register, count, slave=self.address
            )
        except ModbusException as e:
            if self.verbose:
                print("Modbus Exception on read registers", e)
        client.close()
        return self._get_payload(response, verbose=self.verbose)

    async def write_register(self, register: int, value: int) -> bytes:
        """Write the data value to the register"""
        response: Union[ModbusResponse, None] = None
        client = AsyncModbusSerialClient(**modbus_config(self.con_params))
        await client.connect()
        try:
            response = await client.write_register(register, value, slave=self.address)
        except ModbusException as e:
            if self.verbose:
                print("Modbus Exception on write register", e)
        client.close()
        return self._get_payload(response, verbose=self.verbose)
