"""RS-485 module"""

from typing import Union
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
