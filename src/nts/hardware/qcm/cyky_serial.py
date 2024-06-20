"""Functions to communicate with CYKY thickness monitor TM106B"""

from typing import Union
import struct
import time
from serial import Serial  # type: ignore

from .materials import materials
from ..rs485.serial import lrc, check_lrc


class QTM:
    """Quartz crystal thickness monitor"""

    # pylint: disable=too-many-public-methods

    def __init__(
        self, con_params: dict, address: int = 1, retries: int = 5, verbose=False
    ):
        self.con_params = con_params
        self.address = address
        self.retries = retries
        self.response_delay = 5e-3
        self.verbose = verbose

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
    def _get_payload(response: Union[bytes, None], verbose: bool = True) -> bytes:
        """Get the payload from the QTM response"""
        if response:
            # skip start and stop bytes and parse as a hex string
            payload = bytes.fromhex(response[1:-2].decode("utf-8"))
            if check_lrc(payload):
                return payload
            if verbose:
                print(f"LRC mismatch {payload[-1]} != {check_lrc(payload)}")
        return b""

    @staticmethod
    def _parse_response(response: bytes, verbose: bool = True) -> dict:
        """QTM response parser"""
        if verbose:
            print(f"Parsing response: {response!r}")
        parsed: dict = {
            "lrc": 0,
            "addr": -1,  # 0 is reserved for MODBUS as a broadcast address
            "cmd": 0,
            "data_length": 0,
            "register": 0,
            "count": 0,
            "data": tuple(),
        }
        if not response:
            if verbose:
                print("Empty response")
            return parsed
        parsed["lrc"] = response[-1]
        parsed["addr"] = response[0]
        parsed["cmd"] = response[1]
        if parsed["cmd"] == 3:
            parsed["data_length"] = response[2]
            parsed["count"] = int(parsed["data_length"] / 2)
            parsed["data"] = struct.unpack(">" + "h" * parsed["count"], response[3:-1])
            if verbose:
                print(
                    f"CMD: {parsed['cmd']}, ADDR: {parsed['addr']}, LEN: {parsed['count']}, "
                    f"DATA: {parsed['data']}, LRC: {parsed['lrc']}"
                )
        elif parsed["cmd"] == 6:
            parsed["data_length"] = 2
            parsed["count"] = 1
            parsed["register"] = response[2]
            parsed["data"] = (response[3],)
            if verbose:
                print(
                    f"CMD: {parsed['cmd']}, ADDR: {parsed['addr']}, REG: {parsed['register']}, "
                    f"DATA: {parsed['data']}, LRC: {parsed['lrc']}"
                )
        return parsed

    def read_registers(self, start_register: int = 0, count: int = 1) -> bytes:
        """Read QTM registers data"""
        con: Serial
        cmd_code: int = 3
        msg: bytes = self._prepare_message(
            self.address, cmd_code, start_register, count
        )
        if self.verbose:
            print(f"MSG: {msg!r}")
        con = Serial(**self.con_params)
        con.write(msg)
        time.sleep(self.response_delay)
        response: bytes = con.readline()
        con.close()
        return self._get_payload(response, verbose=self.verbose)

    def read_parse_registers(self, start_register: int = 0, count: int = 1) -> dict:
        """Read registers and return parsed response"""
        for iteration in range(self.retries):
            if self.verbose:
                print(f"Iteration {iteration + 1} of {self.retries}")
            response = self.read_registers(start_register=start_register, count=count)
            parsed = self._parse_response(response, verbose=self.verbose)
            if parsed["addr"] == self.address:
                return parsed
        return self._parse_response(b"", verbose=self.verbose)

    def write_register(self, register: int, value: int) -> bytes:
        """Write the data value to the register"""
        con: Serial
        cmd_code: int = 6
        msg: bytes = self._prepare_message(self.address, cmd_code, register, value)
        if self.verbose:
            print(f"MSG: {msg!r}")
        con = Serial(**self.con_params)
        con.write(msg)
        time.sleep(self.response_delay)
        response: bytes = con.readline()
        con.close()
        return self._get_payload(response, verbose=self.verbose)

    def write_parse_register(self, register: int, data: int = 0) -> dict:
        """Write the data value to the register and return parsed response"""
        for iteration in range(self.retries):
            if self.verbose:
                print(f"Iteration {iteration + 1} of {self.retries}")
            response = self.write_register(register=register, value=data)
            parsed = self._parse_response(response, verbose=self.verbose)
            if parsed["addr"] == self.address:
                return parsed
        return self._parse_response(b"", verbose=self.verbose)

    def get_single_register_float(self, register: int, factor: int = 100) -> float:
        """Parse a float number from the register data value divided by provided factor"""
        response: dict = self.read_parse_registers(register, 1)
        if response["data"]:
            return float(response["data"][0] / factor)
        return 0.0

    def get_two_registers_data(self, start_register: int, factor: int = 100) -> float:
        """Parse a float number from the data split between two registers"""
        response: dict = self.read_parse_registers(start_register, 2)
        if response["data"]:
            return float(((response["data"][0] << 16) + response["data"][1]) / factor)
        return 0.0

    def get_version(self) -> float:
        """get QTM firmware version"""
        return self.get_single_register_float(0)

    def get_thickness(self) -> float:
        """Parse thickness (Angstrom) value from register data"""
        return self.get_two_registers_data(1)

    def get_rate(self) -> float:
        """Parse rate (Angstrom/s) value from register data"""
        return self.get_two_registers_data(3)

    def get_frequency(self) -> float:
        """Parse frequency (Hz) value from register data"""
        return self.get_two_registers_data(5)

    # PWM function
    def get_pwm(self) -> float:
        """Parse PWM (0.00 - 99.99%) value from register data"""
        return self.get_single_register_float(7)

    def set_pwm(self, pwm: float = 0.0) -> dict:
        """Set PWM value to register"""
        pwm = max(0.0, min(pwm, 99.99))
        return self.write_parse_register(7, int(round(pwm * 100)))

    # CON parameters
    def get_con(self) -> tuple[int, int, int]:
        """
        Parse CON parameters from register data.
        a: 0-11 gate time = a * 100ms
        b: Analog output (b=0 stop, b=1 auto, b=2 manual)
        c: rate calculation algorythm (c=0 immediate, c=1 weighted, c=2 10-average)
        """
        response: dict = self.read_parse_registers(8, 1)
        if response["data"]:
            coded_str = f"{response['data'][0]:04x}"
            a = int(coded_str[0], 16)
            b = int(coded_str[1], 16)
            c = int(coded_str[2], 16)
            if self.verbose:
                print(f"t: {a * 100} ms, PWM mode: {b}, Rate mode: {c}")
            return a, b, c
        return 0, 0, 0

    def set_con(self, a: int = 1, b: int = 1, c: int = 1) -> dict:
        """
        Set CON values to register.
        a: 0-11 gate time = a * 100ms
        b: Analog output (b=0 stop, b=1 auto, b=2 manual)
        c: rate calculation algorythm (c=0 immediate, c=1 weighted, c=2 10-average)
        """
        a = int(round(max(0, min(a, 11))))
        b = int(round(max(0, min(b, 2))))
        c = int(round(max(0, min(c, 2))))
        value = int(f"0x{a:x}{b:x}{c:x}0", 16)
        return self.write_parse_register(8, value)

    # RUN parameters
    def get_run(self) -> tuple[int, int]:
        """
        Parse measurement run status.
        (x, y) X: running status, Y: film thickness measurement reset.
        x=0 stopped, x=1 started; y=0 no thickness reset, y=1 thickness reset.
        """
        response: dict = self.read_parse_registers(9, 1)
        if response["data"]:
            coded_str: str = f"{response['data'][0]:04x}"
            y = int(coded_str[2], 16)
            x = int(coded_str[3], 16)
            if self.verbose:
                print(f"X: {x}, Y: {y}")
            return x, y
        return 0, 0

    def set_run(self, x: int = 0, y: int = 0) -> dict:
        """
        Parse running status.
        (x, y) X: running status, Y: film thickness measurement reset.
        x=0 stop, x=1 start; y=0 no reset, y=1 reset.
        """
        x = max(0, min(x, 1))
        y = max(0, min(y, 1))
        data = int(f"0x00{int(y):x}{int(x):x}", 16)
        return self.write_parse_register(9, data)

    def start_measurement(self) -> dict:
        """quick method to start measurement"""
        return self.set_run(1, 1)

    def stop_measurement(self) -> dict:
        """quick method to stop measurement"""
        return self.set_run(0, 0)

    # Density parameter
    def get_density(self) -> float:
        """Parse material density (mg/cc 0.4-99.99) value from register data"""
        return self.get_single_register_float(10)

    def set_density(self, density: float) -> dict:
        """Set material density (mg/cc 0.4-99.99) value to register"""
        density = max(0.4, min(density, 99.99))
        return self.write_parse_register(10, int(round(density * 100)))

    # Sound impedance parameter
    def get_sound(self) -> float:
        """Parse sound impedance (Z-ratio) (0.1-9.999) value from register data"""
        return self.get_single_register_float(11, factor=1000)

    def set_sound(self, sound: float) -> dict:
        """Set sound impedance (Z-ratio) (0.1-9.999) value to register"""
        sound = max(0.1, min(sound, 9.999))
        return self.write_parse_register(11, int(round(sound * 1000)))

    # Scale parameter
    def get_scale(self) -> float:
        """Parse scale factor (1-65.535) value from register data"""
        return self.get_single_register_float(12, factor=1000)

    def set_scale(self, scale: float) -> dict:
        """Set scale factor (1-65.535) value to register"""
        scale = max(1.0, min(scale, 65.535))
        return self.write_parse_register(12, int(round(scale * 1000)))

    # Measurement range parameter
    def get_range(self) -> int:
        """Parse range parameter (0-9999 A/s) value from register data"""
        return int(self.get_single_register_float(13, factor=1))

    def set_range(self, rate_range: int) -> dict:
        """Set range parameter (0-9999) value to register"""
        rate_range = max(0, min(rate_range, 9999))
        return self.write_parse_register(13, int(round(rate_range)))

    # RS485 address parameter
    def get_address(self) -> int:
        """Parse RS-485 address (0-254) value from register data"""
        return int(self.get_single_register_float(14, factor=1))

    def set_address(self, address: int) -> dict:
        """Set RS-485 address (1-254) value to register"""
        address = max(1, min(address, 254))
        return self.write_parse_register(14, int(address))

    # RS485 bitrate parameter
    @staticmethod
    def _code_to_baudrate(code: int) -> int:
        """get baudrate value for a given register code (0-5)"""
        baudrate = 0
        if code == 0:
            baudrate = 1200
        elif code == 1:
            baudrate = 2400
        elif code == 2:
            baudrate = 4800
        elif code == 3:
            baudrate = 9600
        elif code == 4:
            baudrate = 19200
        elif code == 5:
            baudrate = 38400
        return baudrate

    @staticmethod
    def _baudrate_to_code(baudrate: int) -> int:
        """Get a register code (0-5) for a given baudrate value"""
        code: int = 3  # default code is 3, which is 9600
        if baudrate == 1200:
            code = 0
        elif baudrate == 2400:
            code = 1
        elif baudrate == 4800:
            code = 2
        elif baudrate == 9600:
            code = 3
        elif baudrate == 19200:
            code = 4
        elif baudrate == 38400:
            code = 5
        return code

    def get_baudrate(self) -> int:
        """Parse RS-485 baudrate value from register data"""
        response: dict = self.read_parse_registers(9, 1)
        code: int = 0
        if response["data"]:
            coded_str: str = f"{response['data'][0]:04x}"
            code = int(coded_str[0], 16)
        return self._code_to_baudrate(code)

    def set_baudrate(self, baudrate: int) -> dict:
        """Set RS-485 baudrate value to register"""
        return self.write_parse_register(15, self._baudrate_to_code(baudrate))

    # Get QTM state in single request
    def get_state(self) -> dict:
        """QTM state in a single request"""
        response: dict = self.read_parse_registers(0, 16)
        state: dict = {
            "version": 0.0,
            "thickness": 0.0,
            "rate": 0.0,
            "frequency": 0.0,
            "pwm": 0.0,
            "con": (0, 0, 0),
            "run": (0, 0),
            "den": 0.0,
            "sound_resistance": 0.0,
            "scale": 0.0,
            "range": 0,
            "addr": 0,
            "baudrate": 0,
        }
        if response["data"]:
            state["version"] = response["data"][0] / 100
            state["thickness"] = (
                (response["data"][1] << 16) + response["data"][2]
            ) / 1e2
            state["rate"] = ((response["data"][3] << 16) + response["data"][4]) / 1e2
            state["frequency"] = (
                (response["data"][5] << 16) + response["data"][6]
            ) / 1e2
            state["pwm"] = response["data"][7] / 100
            con_str = f"{response['data'][8]:04x}"
            state["con"] = (
                int(con_str[0], 16),
                int(con_str[1], 16),
                int(con_str[2], 16),
            )
            run_str = f"{response['data'][9]:04x}"
            state["run"] = (int(run_str[3], 16), int(run_str[2], 16))
            state["den"] = response["data"][10] / 100
            state["sound_resistance"] = response["data"][11] / 1000
            state["scale"] = response["data"][12] / 1000
            state["range"] = response["data"][13]
            state["addr"] = response["data"][14]
            bitrate_str = f"{response['data'][15]:04x}"
            state["baudrate"] = self._code_to_baudrate(int(bitrate_str[0], 16))
        return state

    def set_material(self, material: str = "Au") -> None:
        """Set deposition material density and Z-ratio"""
        den: float = materials[material]["density"]
        snd: float = materials[material]["sound"]
        self.set_density(den)
        time.sleep(self.response_delay)
        self.set_sound(snd)
        time.sleep(self.response_delay)
