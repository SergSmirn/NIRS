import logging
from multiprocessing import freeze_support
from logic.models import Experiment
from logic import logic
from NIRS.celery import app
from matplotlib import pyplot as plt
import numpy as np


@app.task
def run_calc(exp_id):
    exp = Experiment.objects.get(pk=exp_id)
    freeze_support()
    exp.par1, exp.par2 = logic.cross_section_fit(exp)
    print('Found par1 = {0}, par2 = {1}'.format(exp.par1, exp.par2))
    if exp.sim_type == 'monte_carlo':
        exp.simulation_result = logic.run_monte_carlo(exp)
    elif exp.sim_type == 'analytical':
        exp.simulation_result = logic.run_analytical(exp)
    print(exp.simulation_result)

    # fig, ax1 = plt.subplots()
    # plt.gca().set_xscale('log')
    # ax1.plot(exp.simulation_result[0], exp.simulation_result[1], 'bo')
    # plt.show()

    # calculate SER value
    ser = logic.calculate_ser(exp.simulation_result, np.array(exp.spectre))
    print("SER = {0}".format(ser))
    exp.save()
