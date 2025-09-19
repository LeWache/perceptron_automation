from qgor import Station, SingleShotParameter, ArbitraryOriginVector
import time
import numpy as np
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

options = {
    "database": "/home/proteox/Desktop/qgor_db/",
    "experiment": "testing_bias",
    "instruments": {
        "double_qdac": {
            "options": "/home/proteox/PycharmProjects/qgor/qgor/drivers/qdac2/double_qdac.json",
            "load": 1
        },
        "double_qswitch": {
            "options": "/home/proteox/PycharmProjects/qgor/qgor/drivers/qswitch/double_qswitch_options.json",
            "load": 1
        },
        "alazar": 0,
        "rigol_dmm": 1
    },
}


station = Station(options=options, options_path=None)
rigol = station.rigol_dmm
dac = station.double_qdac
switch = station.double_qswitch

def initialize_connections_ohmics():
    switch.prepare_for_sending(18)
    switch.read_line_with_bnc(47, 1)
    switch.unground_line(21, 35)