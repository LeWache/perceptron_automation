import os
import numpy as np



def get_dac_state_as_array():
    string_dac = np.empty(48, dtype='U32')
    for i in range(1,49):
        dac_meas = getattr(dac, f"dac{i}")
        voltage = dac_meas()
        string_dac[i-1] = f"dac_{i:02}: {voltage:.5f}"
    return string_dac

# --- Visualization Functions ---


def prepare_fig_4p():
    """
    Prepare a 4-panel plot for live training visualization.
    """
    plt.rcParams.update({'font.size': 12})
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 8))
    return fig, (ax1, ax2, ax3, ax4)


def plot_training_4p(fig, ax1, ax2, ax3, ax4, i, weight, lbl_in, lbl_out, error):
    """
    Update 4-panel training figure with new iteration data.
    """
    x = np.arange(i)

    ax1.cla()
    ax2.cla()
    ax3.cla()
    ax4.cla()

    ax1.grid()
    ax1.set_ylabel('Weight (a.u.)')
    ax1.plot(x, weight, '-ob')

    ax2.grid()
    ax2.set_ylabel('Label in (a.u.)')
    ax2.plot(x, lbl_in, '-or')

    ax3.grid()
    ax3.plot(x, lbl_out, '-og')
    ax3.set_ylabel('Label out (a.u.)')

    ax4.grid()
    ax4.set_xlabel('Error (#)')
    ax4.plot(x, error, '-ok')
    ax4.set_ylabel('Loss')

    fig.canvas.draw()
    fig.canvas.flush_events()


# --- Data Saving Function ---

def get_path_fits(beta):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Perceptron", "Sonalis")
    folder_path = os.path.join(desktop_path,  f"_b_{beta:.2f}_")
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def get_path_data(beta, w0, eta, method, data_type):

    ext = data_type.lstrip('.')

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Perceptron", "Sonalis", f"_b_{beta:.2f}_")
    folder_name = f"w0_{w0}__e_{eta}__m_{method}"
    folder_path = os.path.join(desktop_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    existing_trials = [
        int(match.group(1)) for filename in os.listdir(folder_path)
        if (match := re.match(fr"trial_(\d+)\.{ext}$", filename))
    ]
    trial = max(existing_trials) + 1 if existing_trials else 1

    name = f'trial_{trial}' + data_type
    file_path = os.path.join(folder_path, name)
    return file_path

def save_data_training(n_iterations, weights, currents, labels, outputs, errors, index_learnt,
                       beta, w0, eta, threshold, method):
    """
    Save training data and metadata to file, auto-incrementing trial index.
    """

    file_path = get_path_data(beta, w0, eta, method, '.txt')

    iterations = np.linspace(1, n_iterations, n_iterations)
    data = np.column_stack((iterations, weights, currents, labels, outputs, errors))

    comment_line = f"w0 = {w0}\teta = {eta}\tbeta\t{beta}\tindex_learnt = {index_learnt}\tthreshold = {threshold}"
    column_header = 'n_iteration\tweight\tcurrent\tlabel_in\tlabel_out\tloss'

    np.savetxt(file_path, data, delimiter='\t', fmt=('%.0f', '%.6f', '%.6f', '%d', '%.3f', '%.4f'), header=f"{comment_line}\n{column_header}")
    print(f"Data saved to: {file_path}")

def save_plot(path):
    os.makedirs(path, exist_ok=True)
    plot_path = os.path.join(path, "figure.png")
    plt.savefig(plot_path)
    print(f"Plot saved to: {plot_path}")