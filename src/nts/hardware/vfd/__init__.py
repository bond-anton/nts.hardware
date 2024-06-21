"""VFD control module"""

from typing import Union
import asyncio
from enum import Enum
from pydantic import BaseModel

from ..rs485 import SerialConnectionConfig, ModbusSerialConnectionConfig


class VFDState(Enum):
    """Possible states of the VFD"""

    STOPPED = "Stopped"
    ACCELERATING = "Accelerating"
    DECELERATING = "Decelerating"
    RUNNING = "Running"


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


class VFD:
    """VFD control base class"""

    # pylint: disable=too-many-public-methods

    def __init__(
        self,
        con_params: Union[SerialConnectionConfig, ModbusSerialConnectionConfig],
        address: int = 1,
        retries: int = 5,
        error_codes: Union[dict[int, VFDError], None] = None,
        verbose=False,
    ):
        # pylint: disable=too-many-arguments
        self.con_params: Union[SerialConnectionConfig, ModbusSerialConnectionConfig] = (
            con_params
        )
        self.address: int = address
        self.retries: int = retries
        self.error_codes: dict[int, VFDError]
        if error_codes is None:
            self.error_codes = {0: VFDError(code=0, message="No error")}
        self.response_delay: float = 5e-3
        self.verbose: bool = verbose

    # Errors processing methods
    async def read_error_code(self) -> int:
        """Read error code from the VFD"""
        await asyncio.sleep(self.response_delay)
        return 0

    def parse_error_code(self, code: int) -> VFDError:
        """Parse error code from the VFD"""
        if code in self.error_codes:
            return self.error_codes[code]
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

    # VFD Control methods
    async def start(self) -> None:
        """Start the VFD"""
        await asyncio.sleep(self.response_delay)

    async def stop(self) -> None:
        """Start the VFD"""
        await asyncio.sleep(self.response_delay)
