from dataclasses import dataclass
from typing import Any
from qgor import Station

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@dataclass
class Context:
    station: Station
    dac: Any = None
    rigol: Any = None
    switch: Any = None


def initialise():
    """
    Initializes the hardware and assigns global objects for station, rigol, dac, and switch.
    """

    options = {
        "database": "/home/proteox/Desktop/qgor_db/",
        "experiment": "Virtualise_and_find_peaks",
        "instruments": {
            "double_qdac": {
                "options": "/home/proteox/PycharmProjects/PythonProject/JSON-perceptron/dac.json",
                "load": 1
            },
            "double_qswitch": {
                "options": "/home/proteox/PycharmProjects/PythonProject/JSON-perceptron/switch.json",
                "load": 1
            },
            "alazar": 0,
            "rigol_dmm": 1
        },
    }

    station = Station(options=options, options_path=None)

    dac = station.double_qdac
    switch = station.double_qswitch
    rigol = station.rigol_dmm

    return Context(station=station, switch=switch, dac=dac, rigol=rigol)