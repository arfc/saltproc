#!/usr/bin/python
"""Sparger Sensitivity Analysis
===============================

This script allows the user to find the optimum designs for optimal
sparger (bubble generator) and entraintment separator efficiency of
molten salt breeder reactor. The script will put all output/plots
into 'data' directory under the working directory. Results are provided
in results.cvs file.

This main script requires that \n
'pandas'\n
'numpy'\n
'matplotlib'\n
'itertools'\n
be installed within the Python environment you are running this script in.

Use following command to make sensitivity analysis,

python sensitivity.py

"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
sys.path.append('../../saltproc/')

from itertools import product
from sparging import Sparger
from sparging import Separator


def referans_design():
    """Referans sparger design based on Jiaqi's simulation
    Parameters
    ----------
    Q_salt : float
        volumetric salt flow rate (m3/s)
    Q_He : float
        volumetric helium flow rate (m3/s)
    L : float
        sparger/contractor length (m)
    ds : float
        sparger/contractor (pipe) diameter (m)
    db : float
        bubble diameter (m) for bubble generator/separator
    Tsalt : float
        salt temperature (K)

    """

    Q_salt = 0.1
    Q_He = Q_salt * 0.05  # up to 5% of total salt flow rate
    L = 10
    ds = 0.1
    db = 0.001
    Tsalt = 900

    param_dict = {'Q_salt': Q_salt, 'Q_He': Q_He,
                  'L': L, 'ds': ds, 'db': db, 'Tsalt': Tsalt}

    return param_dict


def sensitivity():
    """Sensitivity Analysis for Sparger Sysytem

    This script allows the user to find the optimum designs for optimal
    total removal efficiency of molten salt breeder reactor.

    """

    param_dict = referans_design()
    sen_coeff = np.array([0.5, 0.75, 1.0, 1.5, 2])

    for key, value in param_dict.items():
        param_dict[key] = value * sen_coeff

    results = []
    # print([value for key, value in param_dict.items()])

    for comb in product(*[value for key, value in param_dict.items()]):
        eff = dict(zip(param_dict.keys(), comb))
        eff.update(Sparger(*comb).eff())
        results.append(eff)

    df = pd.DataFrame(results)
    df.to_csv('results.csv', header=True, index=True)


def plot_result():
    """This function plots change in performance metrics of sparging system
    with sensitivity parameters for sensitivity analysis.

    """

    pdict = referans_design()
    pltdict = {'Q_salt': {'xaxis': 'salt flow rate ${(m^3/s)}$',
                          'fname': 'salt_flow_rate',
                          'ref': pdict['Q_salt']},
               'Q_He': {'xaxis': 'Helium flow rate ${(m^3/s)}$',
                        'fname': 'helium_flow_rate',
                        'ref': pdict['Q_He']},
               'L': {'xaxis': 'sparger pipe length ${(m)}$',
                     'fname': 'sparger_pipe_length',
                     'ref': pdict['L']},
               'ds': {'xaxis': 'sparger pipe diameter ${(m)}$',
                      'fname': 'sparger_pipe_diameter',
                      'ref': pdict['ds']},
               'db': {'xaxis': 'bubble diameter ${(m)}$',
                      'fname': 'bubble_diameter',
                      'ref': pdict['db']},
               'Tsalt': {'xaxis': 'average salt temperature ${(K)}$',
                         'fname': 'average_salt_temperature',
                         'ref': pdict['Tsalt']}}

    for key, value in pltdict.items():
        df = pd.read_csv('results.csv')

        for par, res in pltdict.items():
            if key != par:
                df = df.loc[df[par] == res['ref']]

        xdata = (df[key]).to_list()
        ydata = (df['Xe']*100).to_list()

        fig = plt.figure(figsize=(5, 5))
        plt.plot(xdata, ydata, 'bo', linestyle="--")
        plt.xlabel(value['xaxis'])
        plt.ylabel("Xe removal effficiency (%)")
        plt.ticklabel_format(axis="x", style="sci", scilimits=(-2, 4))
        figname = str('Xe_eff_vs_%s' % (value['fname']))
        ftype = 'png'
        plt.savefig(figname+'.'+ftype, dpi=300, format=ftype,
                    bbox_inches='tight')
        plt.close()


if __name__ == '__main__':

    sensitivity()
    plot_result()
