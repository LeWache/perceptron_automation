import numpy as np
from scipy.signal import find_peaks
from qgor.tuning_methods import tune_max_gradient
from qgor import ArbitraryOriginVector

from utilities import *

def _get_max_gradient_from_handler(handler, peaks_filter = 0.95):
    roles = get_roles(handler.metadata)
    data = getattr(handler, roles.get('measured'))
    d_data = np.abs(np.diff(data))
    max_peak = np.max(d_data)
    peaks = np.array(np.argwhere(d_data >= peaks_filter * max_peak))

    x_peak, y_peak = np.empty(peaks.shape[0]), np.empty(peaks.shape[0])
    set1, set2 = get_set_variables(handler.metadata)

    variable1 = getattr(handler, set1)
    variable2 = getattr(handler, set2)

    for i, peak in enumerate(peaks):
        x_peak[i] = variable1[peak[0]]
        y_peak[i] = variable2[peak[1]]

    return x_peak, y_peak

def _get_gradient_around_peak(variable_sweep, steps=250, range_sweep=20):
    # variable_1(x_peak)
    # variable_2(y_peak)

    handler = do1d_around(variable_sweep, -range_sweep, range_sweep, steps=steps)

    roles = get_roles(handler.metadata)
    data = getattr(handler, roles.get('measured'))
    d_data = np.diff(data)

    set = get_set_variables(handler.metadata)
    x_data = getattr(handler, set)

    return x_data, d_data

def _get_peaks(x_data, y_data):
    peaks = find_peaks(y_data)
    return peaks, x_data[peaks]

def _points_to_tune_from_peaks(peaks, x_p, range_sweep):

    points_to_tune = []

    if peaks >1:
        for i in range(1, peaks):
            points_to_tune.append( (x_p[i] + x_p[i-1])/2 )

    elif peaks == 1:
        points_to_tune.append( x_p[0] + range_sweep/2)
    # elif peaks == 0:
    #     Exception("There are no peaks!")
    return np.array(points_to_tune)

def find_peaks_and_tune(variable_tune1, variable_tune2,
                        x_set, x_range, y_set, y_range, points, measure_device,
                        range_sweep,
                        range_tuning_sensor = 15, point_tuning_sensor = 100,
                        range_1=3, range_2=0.3, points_tune=150,
                        range_sweep_detuning=10, points_sweep_detuning=100):

    x_start = x_set()
    y_start = y_set()

    handler = station.do2d(x_set, x_start - x_range/2, x_start + x_range/2, points,
                           y_set, y_start - y_range/2, y_start + y_range/2, points,
                           measure_device.do0d, close_when_done=True, x_sleep_time=0.05)

    x_peaks, y_peaks = _get_max_gradient_from_handler(handler, peaks_filter=0.8)

    for i, (x, y) in enumerate(zip(x_peaks, y_peaks)):
        x_set(x), y_set(y)

        voltage_sweep, gradient = _get_gradient_around_peak(variable_tune1)
        max_grad, v_data = _get_peaks(voltage_sweep, gradient)

        v_to_tune = _points_to_tune_from_peaks(max_grad, v_data, range_sweep)

        for i, v in enumerate(v_to_tune):
            variable_tune1(v)

            tune_max_gradient(station, variable_tune2, variable_tune2() - range_tuning_sensor/2, variable_tune2() + range_tuning_sensor/2,
                              point_tuning_sensor, measure_device.do0d, close_plot=True)

            coupling = get_coupling(variable_tune1, range_1, points_tune, variable_tune2, range_2, points_tune)

            variable_tune1(v_data[i])

            vector = ArbitraryOriginVector([variable_tune1, variable_tune2], [1, -coupling])
            station.do1d(vector, -range_sweep_detuning, range_sweep_detuning, points_sweep_detuning, measure_device.do0d, close_plot=False)

            





