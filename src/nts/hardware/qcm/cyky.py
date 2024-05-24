"""Functions to communicate with CYKY thickness monitor TM106B"""

from typing import Union
import time
from serial import Serial  # type: ignore

from .materials import materials


def address_to_ascii(address: int = 1) -> str:
    """RS-485 address to ASCII converter"""
    return f"{address:02x}".upper()


def cmd_to_ascii(cmd: int = 0) -> str:
    """RS-485 command to ASCII converter"""
    return f"{cmd:02x}".upper()


def register_to_ascii(data=0):
    """RS-485 register to ASCII converter"""
    return f"{data:04x}".upper()


def lrc_ascii(data: str) -> str:
    """RS-485 LRC calculation"""
    lrc = 0
    for i in range(int(len(data) / 2)):
        lrc += int(data[2 * i : 2 * i + 2], 16)
    lrc = ((lrc ^ 0xFF) + 1) & 0xFF
    return f"{lrc:02x}".upper()


def read_registers_msg(
    addr: int = 1, start_register: int = 0, length: int = 1
) -> bytes:
    """Generates RS-485 read registers command"""
    payload = address_to_ascii(addr) + cmd_to_ascii(3)
    payload += register_to_ascii(start_register)
    payload += register_to_ascii(length)
    lrc = lrc_ascii(payload)
    msg = ":" + payload + lrc + "\r\n"
    return msg.encode("utf-8")


def parse_response(response: bytes, verbose: bool = True) -> dict:
    """Thickness monitor response parsing"""
    if verbose:
        print(response)
    parsed: dict = {}
    payload: str = response[1:-4].decode(encoding="utf-8")
    parsed["lrc"] = response[-4:-2].decode(encoding="utf-8")
    lrc_check = lrc_ascii(payload)
    if lrc_check != parsed["lrc"] and verbose:
        print("LRC mismatch", parsed["lrc"], lrc_check)
    parsed["addr"] = int(response[1:-2][:2].decode(encoding="utf-8"), 16)
    parsed["cmd"] = int(response[1:-2][2:4].decode(encoding="utf-8"), 16)
    parsed["data_length"] = 2
    parsed["registers"] = 1
    parsed["register"] = 0
    parsed["data"] = "0000"
    if parsed["cmd"] == 3:
        parsed["data_length"] = int(response[1:-2][4:6].decode(encoding="utf-8"), 16)
        parsed["registers"] = int(parsed["data_length"] / 2)
        parsed["data"] = response[7:-4].decode(encoding="utf-8")
        if verbose:
            print(
                f"CMD: {parsed['cmd']}, ADDR: {parsed['addr']}, LEN: {parsed['registers']}, "
                f"DATA: {parsed['data']}, LRC: {parsed['lrc']}"
            )
    elif parsed["cmd"] == 6:
        parsed["register"] = int(response[1:-2][4:8].decode(encoding="utf-8"), 16)
        parsed["data"] = response[1:-2][8:12].decode(encoding="utf-8")
        if verbose:
            print(
                f"CMD: {parsed['cmd']}, ADDR: {parsed['addr']}, REG: {parsed['register']}, "
                f"DATA: {parsed['data']}, LRC: {parsed['lrc']}"
            )
    return parsed


# Getters


def get_register_data(register: int, data: str) -> str:
    """get register data by register number"""
    return data[4 * register : 4 * register + 4]


def parse_version(data: str, verbose: bool = True) -> float:
    """Parse version information from register data"""
    version: float = int(data, 16) / 100
    if verbose:
        print(f"v{version}")
    return version


def parse_thickness(data_hi: str, data_lo: str, verbose: bool = True) -> float:
    """Parse thickness (Angstrom) information from register data"""
    thickness: float = int(data_hi + data_lo, 16) / 100
    if verbose:
        print(f"Thickness: {thickness} A")
    return thickness


def parse_rate(data_hi: str, data_lo: str, verbose: bool = True) -> float:
    """Parse deposition rate (Angstrom/s) information from register data"""
    rate: float = int(data_hi + data_lo, 16) / 100
    if verbose:
        print(f"Rate: {rate} A/s")
    return rate


def parse_frequency(data_hi: str, data_lo: str, verbose: bool = True) -> float:
    """Parse frequency (Hz) information from register data"""
    f: float = int(data_hi + data_lo, 16) / 100
    if verbose:
        print(f"Frequency: {f / 1e6} MHz")
    return f


def parse_pwm(data: str, verbose: bool = True) -> float:
    """Parse pwm-output information from register data"""
    pwm_out: float = int(data, 16) / 100
    if verbose:
        print(f"PWM: {pwm_out} %")
    return pwm_out


def parse_con(data: str, verbose: bool = True) -> tuple[int, int, int]:
    """
    Parse CON parameters information from register data.
    a: 0-11 gate time = a * 100ms
    b: Analog output (b=0 stop, b=1 auto, b=2 manual)
    c: rate calculation algorythm (c=0 immediate, c=1 weighted, c=2 10-average)
    """
    a = int(data[0], 16)
    b = int(data[1], 16)
    c = int(data[2], 16)
    if verbose:
        print(f"t: {a * 100} ms, PWM mode: {b}, Rate mode: {c}")
    return a, b, c


def parse_run(data: str, verbose: bool = True) -> tuple[int, int]:
    """
    Parse running status.
    (x, y) X: running status, Y: film thickness measurement reset.
    x=0 stop, x=1 start; y=0 no reset, y=1 reset.
    """
    y: int = int(data[2], 16)
    x: int = int(data[3], 16)
    if verbose:
        print(f"STARTED: {bool(x)}, Thickness RESET: {bool(y)}")
    return x, y


def parse_den(data: str, verbose: bool = True) -> float:
    """Parse deposited material density from register data"""
    den: float = int(data, 16) / 100
    if verbose:
        print(f"Density: {den} mg/cc")
    return den


def parse_sound(data: str, verbose: bool = True) -> float:
    """Parse Z-ratio data for deposited material from registry data"""
    snd: float = int(data, 16) / 100
    if verbose:
        print(f"SND Resistance (Z-ratio): {snd}")
    return snd


def parse_scale(data: str, verbose: bool = True) -> float:
    """Parse scale factor from registry data"""
    scale: float = int(data, 16) / 1000
    if verbose:
        print(f"Scale: {scale}")
    return scale


def parse_range(data: str, verbose: bool = True) -> int:
    """Parse range from registry data"""
    rng: int = int(data, 10)
    if verbose:
        print(f"Range: {rng}")
    return rng


def parse_address(data: str, verbose: bool = True) -> int:
    """Parse RS-485 address from registry data"""
    addr: int = int(data[1:], 10)
    if verbose:
        print(f"Address: {addr}")
    return addr


def parse_bitrate(data: str, verbose: bool = True) -> int:
    """Parse RS-485 bitrate from registry data"""
    value: int = int(data[0], 10)
    bitrate = 0
    if value == 0:
        bitrate = 1200
    elif value == 1:
        bitrate = 2400
    elif value == 2:
        bitrate = 4800
    elif value == 3:
        bitrate = 9600
    elif value == 4:
        bitrate = 19200
    elif value == 5:
        bitrate = 38400
    if verbose:
        print(f"Bitrate: {bitrate}")
    return bitrate


def parse_read_state_data(parsed_response: dict, verbose: bool = True) -> dict:
    """Parse instrument state data"""
    parsed_data = {
        "version": parse_version(
            get_register_data(0, parsed_response["data"]), verbose=verbose
        ),
        "thickness": parse_thickness(
            get_register_data(1, parsed_response["data"]),
            get_register_data(2, parsed_response["data"]),
            verbose=verbose,
        ),
        "rate": parse_rate(
            get_register_data(3, parsed_response["data"]),
            get_register_data(4, parsed_response["data"]),
            verbose=verbose,
        ),
        "frequency": parse_frequency(
            get_register_data(5, parsed_response["data"]),
            get_register_data(6, parsed_response["data"]),
            verbose=verbose,
        ),
        "pwm": parse_pwm(
            get_register_data(7, parsed_response["data"]), verbose=verbose
        ),
        "con": parse_con(
            get_register_data(8, parsed_response["data"]), verbose=verbose
        ),
        "run": parse_run(
            get_register_data(9, parsed_response["data"]), verbose=verbose
        ),
        "den": parse_den(
            get_register_data(10, parsed_response["data"]), verbose=verbose
        ),
        "sound_resistance": parse_sound(
            get_register_data(11, parsed_response["data"]), verbose=verbose
        ),
        "scale": parse_scale(
            get_register_data(12, parsed_response["data"]), verbose=verbose
        ),
        "range": parse_range(
            get_register_data(13, parsed_response["data"]), verbose=verbose
        ),
    }
    addr = parse_address(
        get_register_data(14, parsed_response["data"]), verbose=verbose
    )
    if parsed_response["addr"] != addr and verbose:
        print("Address does not match CMD")
    parsed_data["bitrate"] = parse_bitrate(
        get_register_data(15, parsed_response["data"]), verbose=verbose
    )
    return parsed_data


def get_state(
    con: Serial, addr: int = 1, retries: int = 5, verbose: bool = True
) -> tuple[dict, dict]:
    """Get instrument state"""
    msg: bytes = read_registers_msg(addr=addr, start_register=0, length=16)
    if verbose:
        print(msg)
    iteration: int = 0
    while True:
        iteration += 1
        if verbose:
            print("Iteration", iteration)
        con.write(msg)
        time.sleep(0.005)
        resp_buff: bytes = b""
        for _ in range(3):
            resp_buff = con.readline()
            if resp_buff:
                break
            time.sleep(0.1)
        parsed: dict = {}
        try:
            parsed = parse_response(resp_buff, verbose=verbose)
            if parsed["addr"] == addr and parsed["cmd"] == 3:
                break
        except (TypeError, IndexError, ValueError):
            pass
        if iteration > retries:
            break
        time.sleep(0.1)
    state_data = parse_read_state_data(parsed, verbose=verbose)
    return parsed, state_data


# Setters


# pylint: disable=too-many-arguments
def write_register(
    con: Serial,
    addr: int,
    register: int,
    data: str,
    retries: int = 5,
    verbose: bool = True,
) -> Union[dict, None]:
    """Write register data"""
    if register < 7:
        return None
    payload: str = address_to_ascii(addr) + cmd_to_ascii(6)
    payload += register_to_ascii(register)
    payload += data
    msg: str = ":" + payload + lrc_ascii(payload) + "\r\n"
    iteration: int = 0
    while True:
        iteration += 1
        if verbose:
            print("Iteration", iteration)
        con.write(msg.encode("utf-8"))
        time.sleep(0.005)
        resp_buff: bytes = b""
        for _ in range(3):
            resp_buff = con.readline()
            if resp_buff:
                break
            time.sleep(0.1)
        parsed: dict = {}
        try:
            parsed = parse_response(resp_buff, verbose=verbose)
            if (
                parsed["addr"] == addr
                and parsed["cmd"] == 6
                and parsed["register"] == register
            ):
                break
        except (TypeError, ValueError, IndexError):
            pass
        if iteration > retries:
            break
        time.sleep(0.1)
    return parsed


def set_pwm(
    con: Serial, output: float, addr: int = 1, verbose: bool = True
) -> Union[float, None]:
    """Set PWM output"""
    if output > 99.99:
        output = 99.99
    elif output < 0:
        output = 0
    data: str = f"{round(output * 100):04x}".upper()
    resp: Union[dict, None] = write_register(con, addr, 7, data, verbose=verbose)
    if resp:
        return parse_pwm(resp["data"], verbose=verbose)
    return None


def set_con(
    con: Serial,
    a: int = 10,
    b: int = 1,
    c: int = 1,
    addr: int = 1,
    verbose: bool = True,
) -> Union[tuple[int, int, int], None]:
    """
    Set measurement parameters
    a: 0-11 gate time = a * 100ms
    b: Analog output (b=0 stop, b=1 auto, b=2 manual)
    c: rate calculation algorythm (c=0 immediate, c=1 weighted, c=2 10-average)
    """
    data: str = f"{a:x}{b:x}{c:x}0".upper()
    print(data)
    resp: Union[dict, None] = write_register(con, addr, 8, data, verbose=verbose)
    if resp:
        return parse_con(resp["data"], verbose=verbose)
    return None


def set_run(
    con: Serial, x: int = 0, y: int = 0, addr: int = 1, verbose: bool = True
) -> Union[tuple[int, int], None]:
    """
    Start/stop measurement
    (x, y) X: running status, Y: film thickness measurement reset.
    x=0 stop, x=1 start; y=0 no reset, y=1 reset.
    """
    data: str = f"00{y:x}{x:x}".upper()
    if verbose:
        print(data)
    resp: Union[dict, None] = write_register(con, addr, 9, data, verbose=verbose)
    if resp:
        return parse_run(resp["data"], verbose=verbose)
    return None


def set_den(
    con: Serial, density: float, addr: int = 1, verbose: bool = True
) -> Union[float, None]:
    """Set deposition material density"""
    if density > 99.99:
        density = 99.99
    elif density < 0.4:
        density = 0.4
    data: str = f"{round(density * 100):04x}".upper()
    resp: Union[dict, None] = write_register(con, addr, 10, data, verbose=verbose)
    if resp:
        return parse_den(resp["data"], verbose=verbose)
    return None


def set_sound(
    con: Serial, sound: float, addr: int = 1, verbose: bool = True
) -> Union[float, None]:
    """Set deposition material Z-ratio"""
    if sound > 9.999:
        sound = 9.999
    elif sound < 0.1:
        sound = 0.1
    data: str = f"{round(sound * 100):04x}".upper()
    resp: Union[dict, None] = write_register(con, addr, 11, data, verbose=verbose)
    if resp:
        return parse_sound(resp["data"], verbose=verbose)
    return None


def set_scale(
    con: Serial, scale: float, addr: int = 1, verbose: bool = True
) -> Union[float, None]:
    """Set scale factor"""
    if scale > 65.535:
        scale = 65.535
    elif scale < 0.001:
        scale = 0.001
    data: str = f"{round(scale * 1000):04x}".upper()
    if verbose:
        print(data)
    resp: Union[dict, None] = write_register(con, addr, 12, data, verbose=verbose)
    if resp:
        return parse_scale(resp["data"], verbose=verbose)
    return None


def set_range(
    con: Serial, rng: int, addr: int = 1, verbose: bool = True
) -> Union[int, None]:
    """Set range"""
    if rng > 9999:
        rng = 9999
    elif rng < 1:
        rng = 1
    data: str = f"{round(rng):04d}".upper()
    resp: Union[dict, None] = write_register(con, addr, 13, data, verbose=verbose)
    if resp:
        return parse_range(resp["data"], verbose=verbose)
    return None


def set_addr(
    con: Serial, address: int, addr: int = 1, verbose: bool = True
) -> Union[int, None]:
    """Set RS-485 address"""
    if address > 254:
        address = 254
    elif address < 1:
        address = 1
    data: str = f"{round(address):04d}".upper()
    resp: Union[dict, None] = write_register(con, addr, 14, data, verbose=verbose)
    if resp:
        return parse_address(resp["data"], verbose=verbose)
    return None


def set_bitrate(
    con: Serial, bitrate: int, addr: int = 1, verbose: bool = True
) -> Union[int, None]:
    """Set RS-485 bitrate"""
    value: int = 3
    if bitrate == 1200:
        value = 0
    elif bitrate == 2400:
        value = 1
    elif bitrate == 4800:
        value = 2
    elif bitrate == 9600:
        value = 3
    elif bitrate == 19200:
        value = 4
    elif bitrate == 38400:
        value = 5
    data: str = f"{round(value)}000"
    resp: Union[dict, None] = write_register(con, addr, 15, data, verbose=verbose)
    if resp:
        return parse_bitrate(resp["data"], verbose=verbose)
    return None


def set_material(
    con: Serial, material: str = "Au", addr: int = 1, verbose: bool = True
) -> None:
    """Set deposition material density and Z-ratio"""
    den: float = materials[material]["density"]
    snd: float = materials[material]["sound"]
    set_den(con, den, addr, verbose=verbose)
    time.sleep(0.2)
    set_sound(con, snd, addr, verbose=verbose)
    time.sleep(0.2)
