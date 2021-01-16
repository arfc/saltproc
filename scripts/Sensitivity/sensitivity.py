#!/usr/bin/python
"""Sparger Sensitivity Analysis
===============================

This script allows the user to find the optimum designs for optimal
sparger (bubble generator) and entrainment separator efficiency of
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
sys.path.append('../../')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from itertools import product
from sparging import Sparger
from sparging import Separator


def ref_sparger_design():
    """Reference sparger design based on Jiaqi's simulation
    Constants
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

    Return
    ------
    param_dict: dict
        containing values for reference separator design
    pltdict: dict
        containing parameters for plotting
    """

    Q_salt = 0.1
    Q_He = Q_salt * 0.05  # up to 5% of total salt flow rate
    L = 10
    ds = 0.1
    db = 0.001
    Tsalt = 900

    param_dict = {'Q_salt': Q_salt, 'Q_He': Q_He, 'L': L,
                  'ds': ds, 'db': db, 'Tsalt': Tsalt}
    pltdict = {'Q_salt': {'xaxis': 'salt flow rate ${(m^3/s)}$',
                          'fname': 'salt_flow_rate'},
               'Q_He': {'xaxis': 'helium flow rate ${(m^3/s)}$',
                        'fname': 'helium_flow_rate'},
               'L': {'xaxis': 'sparger pipe length ${(m)}$',
                     'fname': 'sparger_pipe_length'},
               'ds': {'xaxis': 'sparger pipe diameter ${(m)}$',
                      'fname': 'sparger_pipe_diameter'},
               'db': {'xaxis': 'bubble diameter ${(m)}$',
                      'fname': 'bubble_diameter'},
               'Tsalt': {'xaxis': 'average salt temperature ${(K)}$',
                         'fname': 'average_salt_temperature'}
               }

    return param_dict, pltdict


def ref_separator_design():
    """Reference sparger design based on Jiaqi's simulation
    Constants
    ----------
    Qe : float
        liquid flow rate (m3/s)
    Qg : float
        gas flow rate (m3/s)
    Pgamma : float
        pressure at the densitometer station
    X : float
        the gas injection rate
        default: 5% 0f total flow

    Return
    ------
    param_dict: dict
        containing values for reference separator design
    pltdict: dict
        containing parameters for plotting
    """

    Qe = 0.1
    Qg = 0.005
    Pgamma = 10
    X = 0.05

    param_dict = {'Qe': Qe, 'Qg': Qg, 'Pgamma': Pgamma, 'X': X}
    pltdict = {'Qe': {'xaxis': 'liquid flow rate ${(m^3/s)}$',
                      'fname': 'liquid_flow_rate'},
               'Qg': {'xaxis': 'gas flow rate ${(m^3/s)}$',
                      'fname': 'gas_flow_rate'},
               'Pgamma': {'xaxis': 'densitometer pressure ${(Pa)}$',
                          'fname': 'densitometer_pressure'},
               'X': {'xaxis': 'the gas injection rate ${(m)}$',
                     'fname': 'the gas_injection_rate'},
               }

    return param_dict, pltdict


def sensitivity(func, param_dict, fn='results.csv'):
    """Sensitivity Analysis for Sparger System

    This script allows the user to find the optimum designs for optimal
    total removal efficiency of molten salt breeder reactor.

    """
    param_dict = param_dict[0]
    sen_coeff = np.array([0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5])

    for key, value in param_dict.items():
        param_dict[key] = value * sen_coeff

    results = []

    for comb in product(*[value for key, value in param_dict.items()]):
        eff = dict(zip(param_dict.keys(), comb))
        eff.update(func(*comb).eff())
        results.append(eff)

    df = pd.DataFrame(results)
    df.to_csv(fn, header=True, index=True)


def plot_result(param_dict, fn='results.csv'):
    """This function plots change in performance metrics of sparging system
    for sensitivity parameters in sensitivity analysis.

    """
    plt_dict = param_dict[1]
    param_dict = param_dict[0]
    datafile = pd.read_csv(fn)

    #  Individual line plot for each parameter
    for key, value in plt_dict.items():
        df = datafile
        for par, res in plt_dict.items():
            if key != par:
                df = df.loc[df[par] == param_dict[par]]
        xdata = (df[key]).to_list()
        ydata = (df['Xe']*100).to_list()
        plt.figure(figsize=(5, 5))
        plt.plot(xdata, ydata, 'bo', linestyle="--", label='Xe',
                 markerfacecolor='None')
        ydata = (df['Kr'] * 100).to_list()
        plt.plot(xdata, ydata, 'rx', linestyle="-", label='Kr')
        ydata = (df['H'] * 100).to_list()
        plt.plot(xdata, ydata, 'g^', linestyle="dotted", label='H',
                 markerfacecolor='None')
        plt.legend()
        plt.xlabel(value['xaxis'])
        plt.ylabel("removal efficiency (%)")
        plt.ticklabel_format(axis="x", style="sci", scilimits=(-2, 4))
        figname = str('figs/Xe_eff_vs_%s' % key)
        ftype = 'png'
        plt.savefig(figname+'.'+ftype, dpi=300, format=ftype,
                    bbox_inches='tight')
        plt.close()

    #  2-D removal efficiency counter plots for two selected parameters
    sens = [*plt_dict]
    for key1, value1 in plt_dict.items():
        sens.remove(key1)
        for key2 in sens:
            df = datafile
            for par, res in plt_dict.items():
                if key1 != par and key2 != par:
                    df = df.loc[df[par] == param_dict[par]]
            xdata = (df[key1]).to_list()
            ydata = (df[key2]).to_list()
            zdata = (df['Xe'] * 100).to_list()
            plt.tricontourf(xdata, ydata, zdata, 15)
            plt.colorbar()
            plt.title('Xe removal efficiency (%)')
            plt.xlabel(plt_dict[key1]['xaxis'])
            plt.ylabel(plt_dict[key2]['xaxis'])
            plt.ticklabel_format(axis="both", style="sci", scilimits=(-2, 4))
            figname = str('figs/%s_vs_%s' % (key1, key2))
            ftype = 'png'
            plt.savefig(figname + '.' + ftype, dpi=300, format=ftype,
                        bbox_inches='tight')
            plt.close()

    #  United 2-D removal efficiency counter plots for two selected parameters
    sens = [*plt_dict]
    index = 1
    plt.figure(figsize=(16, 32))
    for key1, value1 in plt_dict.items():
        sens.remove(key1)
        for key2 in sens:
            df = datafile
            for par, res in plt_dict.items():
                if key1 != par and key2 != par:
                    df = df.loc[df[par] == param_dict[par]]
            plt.subplot(8, 2, index)
            index += 1
            xdata = (df[key1]).to_list()
            ydata = (df[key2]).to_list()
            zdata = (df['Xe'] * 100).to_list()
            plt.tricontourf(xdata, ydata, zdata, 15)
            plt.colorbar()
            plt.xlabel(plt_dict[key1]['xaxis'])
            plt.ylabel(plt_dict[key2]['xaxis'])
            plt.ticklabel_format(axis="both", style="sci", scilimits=(-2, 4))
            plt.tight_layout()
            figname = 'figs/Xe_removal_eff_' + fn.split(".")[0]
            ftype = 'png'
            plt.savefig(figname + '.' + ftype, dpi=500, format=ftype,
                        bbox_inches='tight')
    plt.close()


if __name__ == '__main__':

    sensitivity(Sparger, ref_sparger_design(), 'results_sparger.csv')
    plot_result(ref_sparger_design(), 'results_sparger.csv')
    sensitivity(Separator, ref_separator_design(), 'results_separator.csv')
    plot_result(ref_separator_design(), 'results_separator.csv')
