#!/usr/bin/python
"""Sparging System Sensitivity Analysis
=======================================

This script allows the user to find the optimum designs for optimal
sparger (bubble generator) and entrainment separator efficiency of
molten salt breeder reactor. The script will put all output/plots
into 'data' directory under the working directory. Results are provided
in result.cvs file.

This main script requires that \n
'pandas'\n
'numpy'\n
'matplotlib'\n
'itertools'\n
be installed within the Python environment you are running this script in.

Use following command to make sensitivity analysis,

python sensitivity.py

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from itertools import product
from sparger import Sparger
from separator import Separator


class Sensitivity(Sparger):
    """Class makes sensitivity analysis for Sparging system.

    Attributes
    ----------
    pc: array
        percent change in the nominal value of a sensitivity param
    tofile: str
        file name for results to be written

        Methods
    -------
    contour(datafile, united)
        Plots counter plots for sensitivity analysis
    line(datafile)
        Plots line plots for sensitivity analysis
    sens()
        Makes sensitivity analysis and plot results
    """

    pc = np.array([-25, -10, 0, 10, 25])
    tofile = 'result.csv'

    def __init__(self):
        super().__init__()

        self.param_dict = {key: self.__dict__[key]
                           for key in self.description().keys()}

    def contour(self, datafile, united=None):
        """This function shows results on a counter plot for parameters
        in sensitivity analysis. Illustrates combined effect of two selected
        parameters on removal efficiency.

        Parameters
        ----------
        datafile: dict dataframe
            sensitivity analysis results in panda dataframe form
        united: any or None
            Unites all individual graphs into a single plot for comparison
            default: None, plots individual counter graphs for each params

        """

        index = 1
        sens = [*self.description()]
        for key1, value1 in self.description().items():
            sens.remove(key1)
            for key2 in sens:
                df = datafile
                for par, res in self.description().items():
                    if key1 != par and key2 != par:
                        df = df.loc[df[par] == self.param_dict[par]]

                #  2-D removal efficiency counter plots
                figname = str('figs/%s_vs_%s' % (key1, key2))

                if united is not None:
                    plt.subplot(8, 2, index)
                    index += 1
                    figname = 'figs/Xe_removal_eff_' + self.tofile.split(".")[0]

                xdata = (df[key1]).to_list()
                ydata = (df[key2]).to_list()
                zdata = (df['Xe'] * 100).to_list()
                plt.tricontourf(xdata, ydata, zdata, 15)
                plt.colorbar()
                plt.title('Xe removal efficiency (%)')
                plt.xlabel(self.description()[key1]['xaxis'])
                plt.ylabel(self.description()[key2]['xaxis'])
                plt.ticklabel_format(axis="both", style="sci",
                                     scilimits=(-2, 4))
                ftype = 'png'
                plt.savefig(figname + '.' + ftype, dpi=300, format=ftype,
                            bbox_inches='tight')
                if united is None:
                    plt.close()

        plt.close()

    def line(self, datafile):
        """This function shows results on a line plot for each parameter
        in sensitivity analysis.
        Parameters
        ----------
        datafile: dict dataframe
            sensitivity analysis results in panda dataframe form
        """

        #  Individual line plot for each parameter
        for key, value in self.description().items():
            df = datafile
            for par, res in self.description().items():
                if key != par:
                    df = df.loc[df[par] == self.param_dict[par]]
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

    def sens(self):
        """Sensitivity Analysis for Sparging System

        This function allows the user to find the optimum designs for optimal
        total removal efficiency of molten salt breeder reactor.
        """

        coeff = {key: value * (1+self.pc/100)
                 for key, value in self.param_dict.items()}

        results = []
        for comb in product(*[value for key, value in coeff.items()]):
            efficiency = dict(zip(coeff.keys(), comb))
            # efficiency.update(Separator(*comb).eff())
            super().__init__(*comb)
            efficiency.update(super().eff())
            results.append(efficiency)

        df = pd.DataFrame(results)
        print(df)
        df.to_csv(self.tofile, header=True, index=True)

        #  Plots of results
        self.line(df)
        self.contour(df)
        plt.figure(figsize=(16, 40))
        self.contour(df, united='united')


if __name__ == '__main__':
    Sensitivity().sens()
