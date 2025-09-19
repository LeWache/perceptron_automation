import numpy as np
from qgor.experiment_code.Perceptron_functions import prepare_fig_4p

from dataclasses import dataclass
from typing import List

@dataclass
class LearningData:
    index: int
    omegas: List[float]
    currents: List[float]
    labels: List[int]
    outputs: List[float]
    losses: List[float]


def error(target, output):
    """
    Quadratic loss function used during training.
    """
    return 1 / 4 * (target - output) ** 2

def update_sonali(omega_i, target, output, eta, params):
    """
    Update rule for weight (omega) in Sonali's perceptron algorithm.
    """
    return omega_i - eta * params[1] * target * (target - output) * (1 - output ** 2) / 2


def learning_sonali(detuning, n_iterations, w0, eta, threshold, current_to_label, params, safety_val):
    """
    Execute online training loop using Sonali's learning rule.
    """
    omegas = np.empty(n_iterations)
    currents = np.empty(n_iterations)
    errors = np.empty(n_iterations)
    labels = np.random.choice([-1, 1], size=n_iterations)
    outputs = np.empty(n_iterations)

    fig, (ax1, ax2, ax3, ax4) = prepare_fig_4p()
    plt.show(block=False)

    for i in tqdm(range(n_iterations), desc="Shh... I'm learning!"):
        omegas[i] = w0 if i == 0 else update_sonali(omegas[i - 1], labels[i - 1], outputs[i - 1], eta, params)
        currents[i] = measure_at_detuning(detuning, labels[i] * omegas[i], safety_val, rigol)
        outputs[i] = current_to_label(currents[i])
        errors[i] = error(labels[i], outputs[i])
        plot_training_4p(fig, ax1, ax2, ax3, ax4, i, omegas[:i], labels[:i], outputs[:i], errors[:i])

    detuning(0)

    indices_learnt = np.where(errors < threshold)[0]
    index_learnt = indices_learnt[0] if len(indices_learnt) > 0 else n_iterations

    return index_learnt, omegas, currents, labels, outputs, errors