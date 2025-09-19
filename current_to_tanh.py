def current_to_label_fit(I, params):
    """
    Normalize current I using fit parameters.
    Offset: params[2], scale: params[3]
    """
    return (I - params[2]) / params[3]


def current_to_label_min_max(I, detuning, safety_val, meas_device):
    """
    Normalize current I using max and min current from symmetric detuning sweep.
    """
    detuning(safety_val)
    time.sleep(0.05)
    max_I = meas_device.do0d()
    detuning(-safety_val)
    time.sleep(0.05)
    min_I = meas_device.do0d()
    return (I - (max_I + min_I) / 2) / ((max_I - min_I) / 2)


def tanh(v, v0, beta, I0, A):
    """
    Standard tanh fit function used for training curves.
    """
    return A * np.tanh(beta * (v - v0)) + I0


def tanh_beta(v, v0, beta):
    """
    Tanh function with beta as only parameter.
    """
    return np.tanh(beta * (v-v0))