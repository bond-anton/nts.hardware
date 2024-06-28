"""Base VFD interfaces"""

from typing import Union
import asyncio
from enum import Enum
from pydantic import BaseModel

from ..rs485 import RS485Client, SerialConnectionConfig, ModbusSerialConnectionConfig


class VFDState(Enum):
    """Possible states of the VFD"""

    UNKNOWN = "Unknown"
    STOPPED = "Stopped"
    RUNNING_FORWARD = "Running forward"
    RUNNING_BACKWARD = "Running reverse"


class VFDError(BaseModel):
    """Model of error code-message"""

    code: int
    message: str


class VFDParameters(BaseModel):
    """VFD parameters model"""

    frequency: float
    frequency_percent: float
    output_current: float = 0.0
    output_voltage: float = 0.0
    output_power: float = 0.0
    started: bool = False
    state: VFDState = VFDState.STOPPED


class VFD(RS485Client):
    """VFD control base class"""

    # pylint: disable=too-many-public-methods

    def __init__(
        self,
        con_params: Union[SerialConnectionConfig, ModbusSerialConnectionConfig],
        address: int = 1,
        retries: int = 5,
        error_codes: Union[dict[int, VFDError], None] = None,
        error_codes_com: Union[dict[int, VFDError], None] = None,
        label: str = "VFD",
    ):
        # pylint: disable=too-many-arguments
        super().__init__(
            con_params=con_params, address=address, retries=retries, label=label
        )
        self.error_codes: dict[int, VFDError]
        self.error_codes_com: dict[int, VFDError]
        if error_codes is None:
            self.error_codes = {0: VFDError(code=0, message="No error")}
        if error_codes_com is None:
            self.error_codes_com = {0: VFDError(code=0, message="No error")}

    # Errors processing methods
    async def read_error_code(self) -> int:
        """Read error code from the VFD"""
        await asyncio.sleep(self.response_delay)
        return 0

    async def read_error_code_com(self) -> int:
        """Read communication error code from the VFD"""
        await asyncio.sleep(self.response_delay)
        return 0

    def parse_error_code(self, code: int) -> VFDError:
        """Parse error code from the VFD"""
        if code in self.error_codes:
            return self.error_codes[code]
        return VFDError(code=code, message="Unknown error")

    def parse_error_code_com(self, code: int) -> VFDError:
        """Parse communication error code from the VFD"""
        if code in self.error_codes_com:
            return self.error_codes_com[code]
        return VFDError(code=code, message="Unknown error")

    async def clear_error(self) -> int:
        """Clear error from the VFD"""
        await asyncio.sleep(self.response_delay)
        return 0

    # Parameters monitoring methods
    async def read_parameters(self) -> VFDParameters:
        """Start the VFD"""
        await asyncio.sleep(self.response_delay)
        return VFDParameters(frequency=0.0, frequency_percent=0.0)

    async def read_state(self) -> VFDState:
        """Start the VFD"""
        await asyncio.sleep(self.response_delay)
        return VFDState.UNKNOWN

    # VFD Control methods
    async def start(self, backward: bool = False, slow: bool = False) -> None:
        """Start the VFD"""
        # pylint: disable=unused-argument
        await asyncio.sleep(self.response_delay)

    async def stop(self, freewheel: bool = False) -> None:
        """Start the VFD"""
        # pylint: disable=unused-argument
        await asyncio.sleep(self.response_delay)
