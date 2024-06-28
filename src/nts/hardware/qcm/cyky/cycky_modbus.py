"""Functions to communicate with CYKY thickness monitor TM106B using pymodbus"""

from .cyky import QTM
from ...rs485 import ModbusSerialConnectionConfig


class QTMModbus(QTM):
    """Quartz crystal thickness monitor"""

    # pylint: disable=too-many-public-methods

    def __init__(
        self,
        con_params: ModbusSerialConnectionConfig,
        address: int = 1,
        retries: int = 5,
        label: str = "QTM",
        **kwargs,
    ):
        super().__init__(
            ModbusSerialConnectionConfig(**con_params.model_dump()),
            address,
            retries,
            label,
            **kwargs,
        )
