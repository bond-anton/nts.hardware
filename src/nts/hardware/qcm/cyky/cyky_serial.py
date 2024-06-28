"""Functions to communicate with CYKY thickness monitor TM106B using pyserial"""

from typing import Union
import asyncio
import struct

from serial import Serial  # type: ignore

from .cyky import QTM
from ...rs485 import SerialConnectionConfig
from ...rs485.serial import lrc, check_lrc


class QTMSerial(QTM):
    """Quartz crystal thickness monitor"""

    # pylint: disable=too-many-public-methods

    def __init__(
        self,
        con_params: SerialConnectionConfig,
        address: int = 1,
        retries: int = 5,
        label: str = "QTM",
        **kwargs,
    ):
        super().__init__(
            SerialConnectionConfig(**con_params.model_dump()),
            address,
            retries,
            label,
            **kwargs,
        )

    @staticmethod
    def _prepare_message(
        address: int, cmd_code: int, register: int, value: int
    ) -> bytes:
        """Build a message for a QTM (10 bytes)"""
        payload: bytes = struct.pack(
            ">BBh", address, cmd_code, register
        )  # 4 bytes header
        payload += struct.pack(">h", value)  # 2 bytes data
        payload += struct.pack(">B", lrc(payload))  # 1 byte LRC
        return b":" + payload.hex().upper().encode("utf-8") + b"\r\n"  # 3 bytes more

    def _get_serial_payload(self, response: Union[bytes, None]) -> bytes:
        """Get the payload from the QTM response"""
        if response:
            # skip start and stop bytes and parse as a hex string
            payload = bytes.fromhex(response[1:-2].decode("utf-8"))
            if check_lrc(payload):
                return payload
            self.logger.error("LRC mismatch %d != %d", payload[-1], check_lrc(payload))
        return b""

    async def read_registers(self, start_register: int = 0, count: int = 1) -> bytes:
        """Read QTM registers data"""
        con: Serial
        cmd_code: int = 3
        msg: bytes = self._prepare_message(
            self.address, cmd_code, start_register, count
        )
        self.logger.debug("MSG: %s", msg)
        con = Serial(**self.con_params.model_dump())
        con.write(msg)
        await asyncio.sleep(self.response_delay)
        response: bytes = con.readline()
        con.close()
        return self._get_serial_payload(response)

    async def write_register(self, register: int, value: int) -> bytes:
        """Write the data value to the register"""
        con: Serial
        cmd_code: int = 6
        msg: bytes = self._prepare_message(self.address, cmd_code, register, value)
        self.logger.debug("MSG: %s", msg)
        con = Serial(**self.con_params.model_dump())
        con.write(msg)
        await asyncio.sleep(self.response_delay)
        response: bytes = con.readline()
        con.close()
        return self._get_serial_payload(response)
