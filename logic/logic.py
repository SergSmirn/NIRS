import numpy as np
from scipy.optimize import curve_fit, brentq
from multiprocessing import freeze_support, cpu_count
from billiard.pool import Pool
from functools import partial
from .response_voltage import voltage_amplitude
from .response_point import track_charge
from .tracks_gen import create_tracks
import time
import scipy.integrate as integrate
import scipy.interpolate as interpolate


class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # milliseconds
        if self.verbose:
            print('elapsed time: %f ms' % self.msecs)


# SER
def calculate_ser(sim_results, spectre):
    """
    Calculate SER integral using Simposon's rule by interpolating cross-section values
    at points where spectre is defined
    :param sim_results: np.array containing simulation results
    :param spectre: np.array containing LET values, Integral fluence, and Differential fluence
    :return: SER value
    """
    spectre_temp = spectre
    cut_spectre = np.split(spectre_temp, np.where(spectre_temp[:, 0] > 1e5)[0])[0].T  # remove values for LET>100

    cs_interpolation = interpolate.interp1d(sim_results[0], sim_results[1])
    new_cs = cs_interpolation(cut_spectre[0] / 1e3)

    ser = integrate.simps(np.multiply(cut_spectre[2] * 1e3, new_cs), cut_spectre[0] / 1e3)
    return ser


# Simulation
def run_analytical(exp):
    """
    Find cross-section in isotropic field using analytical approximations
    :param device:
    :param let_count: number of LET values
    :return:
    """
    collection_length, threshold_let = exp.par1, exp.par2
    LET_values = np.logspace(-3, 2, exp.let_values_count)
    LET_values[LET_values < threshold_let / 2] = threshold_let / 2
    if exp.model_type == 'point':
        cross_section = (0.26 * (collection_length ** 2) * (np.log(2 * LET_values / threshold_let)) ** 2)
    elif exp.model_type == 'voltage':
        cross_section = (0.1 * (collection_length ** 2) * (np.log(2 * LET_values / threshold_let)) ** 2.42)
    return np.array([np.logspace(-3, 2, exp.let_values_count), cross_section]).tolist()


def run_monte_carlo(exp):
    """
    Run Monte Carlo simulation for chosen device and model.
    :param device: instance of class Device
    :param model: instance of class Model
    :return: returns np.array with columns LET value, mean number of upsets, std_dev, cross-section value
    """

    results = []
    for k in range(exp.trials_count):
        with Timer() as t:
            tracks = create_tracks(exp.geometry, exp.device.process_node * 2e-6, exp.particles_count)
            # TODO implement angles
            results.append(run_trial(exp, tracks))
            print("finished trial %d" % k)
        print("=> elapsed time: %s s" % t.secs)
    raw_results = np.array(results).T
    # TODO save raw results to file
    mean = np.mean(raw_results, axis=1)
    std_dev = np.std(raw_results, axis=1)
    if exp.geometry == 'disk':
        cross_section = (mean * np.pi * ((exp.device.process_node * 2e-6) ** 2)) / \
                        exp.particles_count
    else:
        cross_section = (4 * mean * np.pi * ((exp.device.process_node * 2e-6) ** 2)) / \
                        exp.particles_count
    results = np.array([np.logspace(-3, 2, exp.let_values_count), cross_section, mean, std_dev])
    return results.tolist()


def run_trial(exp, tracks):
    """
    Run Monte Carlo trial for the model
    :param device:
    :param tracks:
    :param let_count: number of LET values
    :return:
    """
    if exp.model_type == 'point':

        collection_length, threshold_let = exp.par1, exp.par2
        charge = partial(track_charge, LET=1, lc=collection_length)
        all_charges = parallel_solve(charge, tracks)
        trial_results = []
        for LET in np.logspace(-3, 2, exp.let_values_count):
            # calculates the difference between collected charge and critical charge
            all_charges_delta = np.array(all_charges) * LET - collection_length * threshold_let * 1.03e-10
            trial_results.append(len(all_charges_delta[all_charges_delta >= 0]))

    elif exp.model_type == 'voltage':

        R, L = exp.par1, exp.par2
        capacitance = exp.device.capacitance
        resistance = exp.device.resistance

        voltage = partial(voltage_amplitude, LET=1, R=R, L=L, capacitance=capacitance,
                          resistance=resistance)
        all_voltages = parallel_solve(voltage, tracks, chunk_size=2000)
        trial_results = []
        for LET in np.logspace(-3, 2, exp.let_values_count):
            # calculates the difference between voltage amplitude and half of supply voltage
            all_voltages_delta = np.array(all_voltages) * LET - exp.device.supply_voltage / 2
            trial_results.append(len(all_voltages_delta[all_voltages_delta >= 0]))

    return trial_results


def parallel_solve(response_function, tracks, chunk_size=200000):
    """
    Find response value for each track using multiprocessing
    :param response_function: function describing circuit response for a chosen model
    :param tracks: list of tracks to solve for
    :param chunk_size: size of tracks list chunk, set to prevent memory overflow
    :return: list of response values for each track
    """
    responses = []
    for chunk in [tracks[i:i + chunk_size] for i in range(0, len(tracks), chunk_size)]:
        pool = Pool(processes=cpu_count())
        r = pool.map_async(response_function, chunk, callback=responses.append)
        r.wait()
        pool.close()
        pool.join()
        print("Chunk finished")
    responses = [item for sublist in responses for item in sublist]
    return responses


# Prepare
def cross_section_fit(exp):
    """
    Find model parameters by performing curve fit to exerimenatal data using a chosen model

    """
    node = exp.device.process_node / 1e3  # convert nm to um
    x_data = exp.experimental_data[0]
    y_data = np.sqrt(exp.experimental_data[1]) * 1e4  # convert cm2 to um

    def linearized_cross_section(LET, *params):  # transform cross-section(LET) function to linearized form
        cross_section = find_cross_section(exp, LET, params, exp.device.supply_voltage)
        return np.sqrt(cross_section) * 1e4

    if exp.model_type == 'point' or exp.sim_type == "analytical":
        parameters, covariance = curve_fit(linearized_cross_section, x_data, y_data, p0=[node, 1],
                                           bounds=([node / 4, 0.01], [node * 4, 60]),
                                           xtol=1e-4, verbose=2, diff_step=0.1)
        parameters[0] = parameters[0] * 1e-4
    elif exp.model_type == 'voltage':
        parameters, covariance = curve_fit(linearized_cross_section, x_data, y_data, p0=[node / 4, node * 4],
                                           bounds=([node / 16, node / 2], [node * 4, node * 8]),
                                           xtol=1e-4, verbose=2, diff_step=0.01)
        parameters = parameters * 1e-4
    return parameters


def find_cross_section(exp, LET_values, parameters, vdd):
    """
    Calculate cross-section for given  values of LET and model-dependent parameters
    :param LET_values: list or np.array of LET values
    :param parameters: fitting parameters (model-dependent)
    :param model: model type (point or voltage)
    :param vdd: supply voltage
    :return: cross-section value in cm2
    """
    if exp.sim_type == "monte_carlo":

        try:
            iterator = iter(LET_values)
        except TypeError:
            LET_values = [LET_values]
        radius_values = []
        f = partial(find_radius, parameters=parameters, model=exp.model_type, vdd=vdd)
        pool = Pool(processes=cpu_count() - 1)
        result = pool.map_async(f, LET_values, callback=radius_values.append)
        result.wait()
        pool.close()
        pool.join()
        radius_values = [item for sublist in radius_values for item in sublist]

    elif exp.sim_type == "analytical":

        L = parameters[0] * 1e-4
        LETth = parameters[1]
        LET_values = np.array(LET_values)
        LET_values[LET_values < LETth] = LETth
        if exp.model_type == 'point':
            radius_values = (L * (np.log(LET_values / LETth)) ** 0.75) / np.sqrt(np.pi)
        elif exp.model_type == 'voltage':
            radius_values = (L * np.log(LET_values / LETth)) / np.pi

    return np.pi * np.array(radius_values) ** 2


def find_radius(LET, parameters, model, vdd):
    """
    Use Brent optimization method to find the radius of the region where upset condition is met for
    the given parameter values
    :param LET: LET value
    :param parameters: fitting parameters (model-dependent)
    :param model: model type (point or voltage)
    :param vdd: supply voltage
    :return: radius value in centimeters
    """
    if model == 'point':
        Lc = parameters[0] * 1e-4
        LETth = parameters[1]
        f = lambda r: track_charge(np.array([[0, r, 0], [0, r, -3e-4]]), LET, Lc) - Lc * LETth * 1.03e-10
    elif model == 'voltage':
        R = parameters[0] * 1e-4
        L = parameters[1] * 1e-4
        f = lambda r: voltage_amplitude(np.array([[0, r, 0], [0, r, -3e-4]]), LET, R, L) - vdd / 2
    if f(0) <= 0:
        radius = 0
    else:
        radius, convergence = brentq(f, 0, 10e-4, rtol=1e-4, full_output=True)
    return radius
