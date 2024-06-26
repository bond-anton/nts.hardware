"""Functions to communicate with CYKY thickness monitor TM106B"""

import asyncio

from ..materials import materials
from ...rs485 import RS485Client


class QTM(RS485Client):
    """Quartz crystal thickness monitor"""

    # pylint: disable=too-many-public-methods

    async def get_version(self) -> float:
        """get QTM firmware version"""
        return await self.read_single_register_float(0)

    async def get_thickness(self) -> float:
        """Parse thickness (Angstrom) value from register data"""
        return await self.read_two_registers_data(1)

    async def get_rate(self) -> float:
        """Parse rate (Angstrom/s) value from register data"""
        return await self.read_two_registers_data(3)

    async def get_frequency(self) -> float:
        """Parse frequency (Hz) value from register data"""
        return await self.read_two_registers_data(5)

    # PWM function
    async def get_pwm(self) -> float:
        """Parse PWM (0.00 - 99.99%) value from register data"""
        return await self.read_single_register_float(7)

    async def set_pwm(self, pwm: float = 0.0) -> float:
        """Set PWM value to register"""
        pwm = max(0.0, min(pwm, 99.99))
        return await self.write_single_register_float(7, pwm)

    # CON parameters
    async def get_con(self) -> tuple[int, int, int]:
        """
        Parse CON parameters from register data.
        a: 0-11 gate time = a * 100ms
        b: Analog output (b=0 stop, b=1 auto, b=2 manual)
        c: rate calculation algorythm (c=0 immediate, c=1 weighted, c=2 10-average)
        """
        response: dict = await self.read_parse_registers(8, 1)
        if response["data"]:
            coded_str = f"{response['data'][0]:04x}"
            a = int(coded_str[0], 16)
            b = int(coded_str[1], 16)
            c = int(coded_str[2], 16)
            self.logger.debug("t: %d ms, PWM mode: %d, Rate mode: %d", a * 100, b, c)
            return a, b, c
        return 0, 0, 0

    async def set_con(self, a: int = 1, b: int = 1, c: int = 1) -> dict:
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
        return await self.write_parse_register(8, value)

    # RUN parameters
    async def get_run(self) -> tuple[int, int]:
        """
        Parse measurement run status.
        (x, y) X: running status, Y: film thickness measurement reset.
        x=0 stopped, x=1 started; y=0 no thickness reset, y=1 thickness reset.
        """
        response: dict = await self.read_parse_registers(9, 1)
        if response["data"]:
            coded_str: str = f"{response['data'][0]:04x}"
            y = int(coded_str[2], 16)
            x = int(coded_str[3], 16)
            self.logger.debug("X: %d, Y: %d", x, y)
            return x, y
        return 0, 0

    async def set_run(self, x: int = 0, y: int = 0) -> dict:
        """
        Parse running status.
        (x, y) X: running status, Y: film thickness measurement reset.
        x=0 stop, x=1 start; y=0 no reset, y=1 reset.
        """
        x = max(0, min(x, 1))
        y = max(0, min(y, 1))
        data = int(f"0x00{int(y):x}{int(x):x}", 16)
        return await self.write_parse_register(9, data)

    async def start_measurement(self) -> dict:
        """quick method to start measurement"""
        return await self.set_run(1, 1)

    async def stop_measurement(self) -> dict:
        """quick method to stop measurement"""
        return await self.set_run(0, 0)

    # Density parameter
    async def get_density(self) -> float:
        """Parse material density (mg/cc 0.4-99.99) value from register data"""
        return await self.read_single_register_float(10)

    async def set_density(self, density: float) -> float:
        """Set material density (mg/cc 0.4-99.99) value to register"""
        density = max(0.4, min(density, 99.99))
        return await self.write_single_register_float(10, density)

    # Sound impedance ratio (Z-ratio)
    async def get_z_ratio(self) -> float:
        """Parse sound impedance ratio (Z-ratio) (0.1-9.999) value from register data"""
        return await self.read_single_register_float(11, factor=1000)

    async def set_z_ratio(self, z_ratio: float) -> float:
        """Set sound impedance ratio (Z-ratio) (0.1-9.999) value to register"""
        z_ratio = max(0.1, min(z_ratio, 9.999))
        return await self.write_single_register_float(11, z_ratio, factor=1000)

    # Scale parameter
    async def get_scale(self) -> float:
        """Parse scale factor (1-65.535) value from register data"""
        return await self.read_single_register_float(12, factor=1000)

    async def set_scale(self, scale: float) -> float:
        """Set scale factor (1-65.535) value to register"""
        scale = max(1.0, min(scale, 65.535))
        return await self.write_single_register_float(12, scale, factor=1000)

    # Measurement range parameter
    async def get_range(self) -> int:
        """Parse range parameter (0-9999 A/s) value from register data"""
        return int(await self.read_single_register_float(13, factor=1))

    async def set_range(self, rate_range: int) -> int:
        """Set range parameter (0-9999) value to register"""
        rate_range = max(0, min(rate_range, 9999))
        return int(await self.write_single_register_float(13, rate_range, factor=1))

    # RS485 address parameter
    async def get_address(self) -> int:
        """Parse RS-485 address (0-254) value from register data"""
        return int(await self.read_single_register_float(14, factor=1))

    async def set_address(self, address: int) -> int:
        """Set RS-485 address (1-254) value to register"""
        address = max(1, min(address, 254))
        new_address = int(await self.write_single_register_float(14, address, factor=1))
        self.address = new_address
        return new_address

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

    async def get_baudrate(self) -> int:
        """Parse RS-485 baudrate value from register data"""
        response: dict = await self.read_parse_registers(15, 1)
        code: int = 0
        if response["data"]:
            coded_str: str = f"{response['data'][0]:04x}"
            code = int(coded_str[0], 16)
        return self._code_to_baudrate(code)

    async def set_baudrate(self, baudrate: int) -> int:
        """Set RS-485 baudrate value to register"""
        code: int = self._baudrate_to_code(baudrate)
        coded_byte: int = int(f"0x{code}000")
        response: dict = await self.write_parse_register(15, coded_byte)
        code = 0
        if response["data"]:
            coded_str: str = f"{response['data'][0]:04x}"
            code = int(coded_str[0], 16)
        new_baudrate = self._code_to_baudrate(code)
        self.con_params.baudrate = new_baudrate
        return new_baudrate

    # Get QTM state in single request
    async def get_state(self) -> dict:
        """QTM state in a single request"""
        response: dict = await self.read_parse_registers(0, 16)
        state: dict = {
            "version": 0.0,
            "thickness": 0.0,
            "rate": 0.0,
            "frequency": 0.0,
            "pwm": 0.0,
            "con": (0, 0, 0),
            "run": (0, 0),
            "den": 0.0,
            "z_ratio": 0.0,
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
            state["z_ratio"] = response["data"][11] / 1000
            state["scale"] = response["data"][12] / 1000
            state["range"] = response["data"][13]
            state["addr"] = response["data"][14]
            bitrate_str = f"{response['data'][15]:04x}"
            state["baudrate"] = self._code_to_baudrate(int(bitrate_str[0], 16))
        return state

    async def set_material(self, material: str = "Au") -> None:
        """Set deposition material density and Z-ratio"""
        den: float = materials[material]["density"]
        z_ratio: float = materials[material]["z_ratio"]
        await self.set_density(den)
        await asyncio.sleep(self.response_delay)
        await self.set_z_ratio(z_ratio)
        await asyncio.sleep(self.response_delay)
