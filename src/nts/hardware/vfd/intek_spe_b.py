"""Intek SPE-B VFD RS485 control routines"""

from .vfd import VFD, VFDError, VFDState, VFDParameters
from ..rs485 import ModbusSerialConnectionConfig


intek_spe_b_error_codes = {
    # VFD errors
    0: VFDError(code=0, message="No error"),
    1: VFDError(code=1, message="Reserved"),
    2: VFDError(code=2, message="Current overload during acceleration"),
    3: VFDError(code=3, message="Current overload during deceleration"),
    4: VFDError(code=4, message="Current overload at constant speed"),
    5: VFDError(code=5, message="Voltage overload during acceleration"),
    6: VFDError(code=6, message="Voltage overload during deceleration"),
    7: VFDError(code=7, message="Voltage overload at constant speed"),
    8: VFDError(code=8, message="Control circuits power failure"),
    9: VFDError(code=9, message="Undervoltage error"),
    10: VFDError(code=10, message="VFD overload"),
    11: VFDError(code=11, message="Motor overload"),
    12: VFDError(code=12, message="Input phase error"),
    13: VFDError(code=13, message="Output phase error"),
    14: VFDError(code=14, message="Overheat of power converter"),
    15: VFDError(code=15, message="External error"),
    16: VFDError(code=16, message="Remote connection error"),
    17: VFDError(code=17, message="Internal contactor failure"),
    18: VFDError(code=18, message="Current sensor failure"),
    19: VFDError(code=19, message="Automatic motor tuning failure"),
    21: VFDError(code=21, message="EEPROM IO error"),
    22: VFDError(code=22, message="VFD hardware error"),
    23: VFDError(code=23, message="Grounding failure"),
    24: VFDError(code=24, message="Reserved"),
    25: VFDError(code=25, message="Reserved"),
    26: VFDError(code=26, message="Total operation timeout"),
    27: VFDError(code=27, message="User error 1"),
    28: VFDError(code=28, message="User error 2"),
    29: VFDError(code=29, message="Power on timeout"),
    30: VFDError(code=30, message="Underloaded error"),
    31: VFDError(code=31, message="PID feedback connection loss"),
    40: VFDError(code=40, message="IGBT current limiter failure"),
    41: VFDError(code=41, message="Running motor switch error"),
    42: VFDError(code=42, message="Speed error"),
    43: VFDError(code=43, message="Over speed error"),
    45: VFDError(code=45, message="Motor overheat error"),
    92: VFDError(code=92, message="Positioning error"),
    94: VFDError(code=94, message="Calculated speed error"),
}


intek_spe_b_error_codes_com = {
    # Communication errors
    0: VFDError(code=0, message="No error"),
    1: VFDError(code=1, message="Wrong password"),
    2: VFDError(code=2, message="Command code error"),
    3: VFDError(code=3, message="CRC error"),
    4: VFDError(code=4, message="Invalid address"),
    5: VFDError(code=5, message="Invalid parameter"),
    6: VFDError(code=6, message="Parameter can not be edited"),
    7: VFDError(code=7, message="System is blocked"),
    8: VFDError(code=8, message="EEPROM write during operation"),
}


class VFDIntekSPEb(VFD):
    """Intek SPE-B VFD over pyModbus"""

    def __init__(
        self,
        con_params: ModbusSerialConnectionConfig,
        address: int = 1,
        retries: int = 5,
        verbose=False,
    ):
        super().__init__(
            con_params=ModbusSerialConnectionConfig(**con_params.model_dump()),
            address=address,
            retries=retries,
            verbose=verbose,
            error_codes=intek_spe_b_error_codes,
            error_codes_com=intek_spe_b_error_codes_com,
        )

    # Errors processing methods
    async def read_error_code(self) -> int:
        """Read error code from the VFD"""
        return int(await self.read_single_register_float(0x8000, 1))

    async def read_error_code_com(self) -> int:
        """Read communication error code from the VFD"""
        return int(await self.read_single_register_float(0x8001, 1))

    async def clear_error(self) -> int:
        """Clear error from the VFD"""
        await self.write_parse_register(0x2000, 7)
        return await self.read_error_code()

    # Parameters monitoring methods
    async def read_parameters(self) -> VFDParameters:
        """Start the VFD"""
        data = await self.read_parse_registers(1000, 6)
        return VFDParameters(
            frequency=data["data"][1], frequency_percent=data["data"][1]
        )

    async def read_state(self) -> VFDState:
        """Start the VFD"""
        state = int(await self.read_single_register_float(0x3000, 1))
        if state == 1:
            return VFDState.RUNNING_FORWARD
        if state == 2:
            return VFDState.RUNNING_BACKWARD
        if state == 3:
            return VFDState.STOPPED
        return VFDState.UNKNOWN

    # VFD Control methods
    async def start(self, backward: bool = False, slow: bool = False) -> None:
        """Start the VFD"""
        cmd: int = 1
        if backward:
            cmd = 4 if slow else 2
        elif slow:
            cmd = 3
        await self.write_parse_register(0x2000, cmd)

    async def stop(self, freewheel: bool = False) -> None:
        """Start the VFD"""
        cmd: int = 5 if freewheel else 6
        await self.write_parse_register(0x2000, cmd)
