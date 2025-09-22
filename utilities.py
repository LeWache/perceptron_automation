from qgor import Station
station = Station()

from robust_gradient import get_coupling_from_handlers

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

def get_coupling(param1, range, steps, param2, range2, steps2, offset = 0, offset2 = 0):
    # param1 being device, param2 being sensor

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

def do1d_around(dac, amount, steps=100):
    start = dac()
    handler = station.do1d(dac, dac() - amount, dac() + amount, steps, rigol.do0d, close_when_done=True)
    dac(start)
    return handler