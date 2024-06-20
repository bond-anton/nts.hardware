"""RS485 communication helper functions"""

import time
from serial import Serial  # type: ignore


def purge_serial_input_buffer(con: Serial, delay: float = 0.05) -> None:
    """Purge the serial communication buffer"""
    while True:
        time.sleep(delay)
        data: bytes = con.readline()
        if not data:
            break


def check_sum(payload: bytes) -> int:
    """Calculate payload data checksum"""
    cs = 0xFFFF
    for data_byte in payload:
        cs ^= data_byte
        for _ in range(8):
            if cs & 0x0001:
                cs = (cs >> 1) ^ 0xA001
            else:
                cs = cs >> 1
    return cs


def lrc(payload: bytes) -> int:
    """Calculate LRC for the payload data"""
    cs: int = 0
    for data_byte in payload:
        cs += int(data_byte)
    cs = ((cs ^ 0xFF) + 1) & 0xFF
    return cs


def check_lrc(message: bytes) -> bool:
    """Check LRS byte at the end of the message"""
    cs: int = message[-1]
    payload: bytes = message[:-1]
    if lrc(payload) == cs:
        return True
    return False
