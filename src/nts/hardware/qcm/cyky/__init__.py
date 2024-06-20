"""Functions to communicate with CYKY thickness monitor TM106B using either pyserial or pymodbus"""

from .cyky_serial import QTMSerial
from .cycky_modbus import QTMModbus
