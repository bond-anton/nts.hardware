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
        verbose=False,
    ):
        super().__init__(
            SerialConnectionConfig(**con_params.model_dump()), address, retries, verbose
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

    @staticmethod
    def _get_serial_payload(
        response: Union[bytes, None], verbose: bool = True
    ) -> bytes:
        """Get the payload from the QTM response"""
        if response:
            # skip start and stop bytes and parse as a hex string
            payload = bytes.fromhex(response[1:-2].decode("utf-8"))
            if check_lrc(payload):
                return payload
            if verbose:
                print(f"LRC mismatch {payload[-1]} != {check_lrc(payload)}")
        return b""

    async def read_registers(self, start_register: int = 0, count: int = 1) -> bytes:
        """Read QTM registers data"""
        con: Serial
        cmd_code: int = 3
        msg: bytes = self._prepare_message(
            self.address, cmd_code, start_register, count
        )
        if self.verbose:
            print(f"MSG: {msg!r}")
        con = Serial(**self.con_params.model_dump())
        con.write(msg)
        await asyncio.sleep(self.response_delay)
        response: bytes = con.readline()
        con.close()
        return self._get_serial_payload(response, verbose=self.verbose)

    async def write_register(self, register: int, value: int) -> bytes:
        """Write the data value to the register"""
        con: Serial
        cmd_code: int = 6
        msg: bytes = self._prepare_message(self.address, cmd_code, register, value)
        if self.verbose:
            print(f"MSG: {msg!r}")
        con = Serial(**self.con_params.model_dump())
        con.write(msg)
        await asyncio.sleep(self.response_delay)
        response: bytes = con.readline()
        con.close()
        return self._get_serial_payload(response, verbose=self.verbose)
