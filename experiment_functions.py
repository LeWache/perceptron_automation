from qgor import ArbitraryOriginVector
from xarray.coding.common import lazy_elemwise_func

from initialise import initialise
import numpy as np
import matplotlib.pyplot as plt

from qgor.tuning_methods import tune_max_gradient

from robust_gradient import estimate_background_gradient

from tqdm.notebook import tqdm
import sys

context = initialise()

dac = context.dac
station = context.station
rigol = context.rigol


def do1d_around(dac, amount, steps=100):
    start = dac()
    handler = station.do1d(dac, dac() - amount, dac() + amount, steps, rigol.do0d, close_when_done=True)
    dac(start)
    return handler

def get_roles(metadata):
    variables = metadata.get('variables')
    out = {}
    for variable, info in variables.items():
        out[info.get('role')] = variable

    return out

def get_set_variables(metadata):
    set_variables = []
    variables = metadata.get('variables')
    for variable, info in variables.items():
        if info.get('role') == 'set':
            set_variables.append(variable)
    return set_variables

def get_gradient_from_handler(handler, n=2):
    metadata = handler.metadata
    roles = get_roles(metadata)
    x_param = roles.get('set')
    y_param = roles.get('measured')

    x_data = getattr(handler, x_param)
    y_data = getattr(handler, y_param)

    gradient = estimate_background_gradient(x_data, y_data)

    return gradient

# def extract_gradient(handler, n=2):
#     metadata = handler.metadata
#     roles = get_roles(metadata)
#     x_param = roles.get('set')
#     y_param = roles.get('measured')
#
#     x_data = getattr(handler, x_param)
#     y_data = getattr(handler, y_param)
#
#     gradient = np.diff(y_data) / np.diff(x_data)
#     std = np.std(gradient)
#     sign = np.sign(np.mean(gradient))
#
#     filtered_gradient = gradient[sign*gradient > sign*(np.mean(gradient)-n*std)]
#
#     return np.mean(filtered_gradient)

def get_coupling(param1, range, steps, param2, range2, steps2, offset = 0, offset2 = 0):
    i = 0
    start_1, start_2 = param1(), param2()
    param1(start_1+offset), param2(start_2+offset2)

    while i < 10:
        handler1 = do1d_around(param1, range, steps)
        handler2 = do1d_around(param2, range2, steps2)

        coupling = get_coupling_from_handlers(handler1, handler2)

        if 0 < coupling < 0.3:
            break

        print('Coupling is bad: ', coupling)
        print('iterations: ', i)
        i+=1
        param1(start_1 + i*range/2)
        param2(start_2 + i*range2/2)

    param1(start_1), param2(start_2)
    return coupling

def get_coupling_from_handlers(handler1, handler2):
    return get_gradient_from_handler(handler1) / get_gradient_from_handler(handler2)
    # return extract_gradient(handler1) / extract_gradient(handler2)

tune_sensor = lambda range=15, points=100: tune_max_gradient(station, dac.dac9, dac.dac9() - range/2, dac.dac9() + range/2, points, rigol.do0d, close_plot=True)
coupling = lambda param1=dac.dac24, range=5, steps=100, param2=dac.dac9, range2=0.4, steps2=100, offset=-7, offset2=0: get_coupling(param1, range, steps, param2, range2, steps2, offset, offset2)


def get_vector():
    val = coupling()
    return ArbitraryOriginVector([dac.dac24, dac.dac9], [1, -val])

def tune_and_scan(range=80, points=50):
    # tune_sensor()
    # coupling_left = coupling(param1 = dac.dac23)
    # coupling_right= coupling(param1 = dac.dac26)
    # print('coupling left: ', coupling_left)
    # print('coupling right: ', coupling_right)
    #
    # handler = station.do2d_compensated(dac.dac23, (-range, range), points, dac.dac26, (-range, range),
    #                                    points, dac.dac9, -coupling_left, -coupling_right, rigol.do0d, sleep_time = 0.1,
    #                                    close_when_done=True)

    tune_sensor()
    start_23, start_26 = dac.dac23(), dac.dac26()
    handler = station.do2d(dac.dac23, start_23 - range/2, start_23 + range/2, points,
                           dac.dac26, start_26 - range/2, start_26 + range/2, points,
                           rigol.do0d, close_when_done=True, x_sleep_time=0.05)

    return handler

def _get_max_gradient_from_handler(handler, filter = 0.95):
    roles = get_roles(handler.metadata)
    data = getattr(handler, roles.get('measured'))
    d_data = np.abs(np.diff(data))
    max_peak = np.max(d_data)
    peaks = np.array(np.argwhere(d_data >= filter*max_peak))

    x_peak, y_peak = np.empty(peaks.shape[0]), np.empty(peaks.shape[0])
    set1, set2 = get_set_variables(handler.metadata)

    variable1 = getattr(handler, set1)
    variable2 = getattr(handler, set2)

    for i, peak in enumerate(peaks):
        x_peak[i] = variable1[peak[0]]
        y_peak[i] = variable2[peak[1]]

    return x_peak, y_peak

def get_peak_and_sweep(handler, filter = 0.75, points = 100, filter_subplot= 0.65):
    x_peak, y_peak = _get_max_gradient_from_handler(handler, filter)
    current = np.empty( (len(x_peak), points))
    bla(handler, filter_subplot)
    for i, (x, y) in enumerate(zip(x_peak, y_peak)):
        print(x, y)
        dac.dac23(x)
        dac.dac26(y)
        dac.dac24()
        detuning = get_vector()
        current[i] = do1d(detuning, -50, 50, points, rigol.do0d, close_when_done=True).rigol_voltage
        detuning(0)
    return current

def bla(handler, filter=0.75):
    roles = get_roles(handler.metadata)
    data = getattr(handler, roles.get('measured'))
    d_data = np.abs(np.diff(data))
    max_peak = np.max(d_data)
    peaks = np.array(np.argwhere(d_data >= filter*max_peak))

    set1, set2 = get_set_variables(handler.metadata)
    variable1 = getattr(handler, set1)
    variable2 = getattr(handler, set2)

    folder = handler.folder

    plt.figure()
    plt.imshow(d_data.T, extent=(variable1[0], variable1[-1], variable2[0], variable2[-1]), origin='lower')
    for i, peak in enumerate(peaks):
        plt.scatter(variable1[peak[0]], variable2[peak[1]], color='r')
    plt.savefig(folder / 'peaks.png')

def one_run(filter = 0.85, points = 40):
    handler = tune_and_scan(range = 40, points = points)
    get_peak_and_sweep(handler, filter)
    return handler

def testing():
    voltages_plunger = np.linspace(2700, 600, 15)
    voltages_barriers = np.linspace(2800, 1200, 10)

    for plunger in voltages_plunger:
        for barrier in voltages_barriers:
            print(plunger, barrier)
            dac.dac9(2044)
            dac.dac24(plunger)
            dac.dac23(barrier)
            dac.dac26(barrier)
            one_run()
            plt.close('all')

