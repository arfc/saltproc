"""Process module"""
import re
from copy import deepcopy
from math import exp
import numpy as np

from saltproc import Materialflow


class Process():
    """Represents an aribtrary processing component that extracts nuclides from
    a material.

    Parameters
    ----------
    mass_flowrate : float
        mass flow rate of the material flow (g/s)
    capacity : float
        maximum mass flow rate of the material flow which current process
        can handle (g/s)
    volume : float
        total volume of the current facility (:math:`cm^3`)
    efficiency : dict of str to float or str

        ``key``
            element name for removal (not isotope)
        ``value``
            removal efficency for the isotope as a weight fraction (float)
            or a function eps(x,m,t,P,L) (str)
    optional_parameter : float
        user can define any custom parameter in the input file describing
        processes and use it in efficiency function

     """

    def __init__(self, *initial_data, **kwargs):
        """ Initializes the Process object.

        """
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def calculate_removal_efficiency(self, nuc_name):
        """Calculate the value of the removal efficiency for a given nuclide
        in this process.

        If the efficiency is a str describing efficiency as a
        function (eps(x,m,t,P,L)), then construct the function and evaluate it.
        Otherwise, it is a float and can be returned.

        Parameters
        ----------
        nuc_name : str
            Name of target nuclide to be removed.

        Returns
        -------
        efficiency : float
            Extraction efficiency for the given nuclide.

        """
        eps = self.efficiency[nuc_name]
        if isinstance(eps, str):
            for attr, value in self.__dict__.items():
                if attr in eps:
                    eps = eps.replace(attr, "self." + str(attr))
        else:
            eps = str(eps)
        efficiency = eval(eps)
        return efficiency

    def check_mass_conservation(self):
        """Checking that Process.outflow + Process.waste_stream is equal
        Process.inflow and the total mass is being conserved. Returns `True` if
        the mass conserved or `False` if its mismatched.
        """
        out_stream = self.outflow + self.waste_stream
        np.testing.assert_array_equal(out_stream, self.inflow)

    def process_material(self, inflow):
        """Updates :class:`Materialflow` object `inflow` by removing target
        nuclides with specific efficiencies in single component of fuel
        reprocessing system and returns waste stream Materialflow object.

        Parameters
        ----------
        inflow : Materialflow obj
            Material flowing into the processing system component.

        Returns
        -------
        waste_stream : Materialflow object
            Waste stream from the reprocessing system component.
        thru_flow : Materialflow object
            Remaining material flow that will pass through the
            reprocessing system component.

        """
        waste_mass = {}
        thru_mass = {}

        total_waste_mass = 0.0
        total_thru_mass = 0.0

        if bool(self.efficiency):
            process_elements = list(self.efficiency.keys())
            process_nucs = [nuc for nuc in inflow.comp.keys() if re.match(r"([A-Z]+)([0-9]+)", nuc, re.I).groups()[0] in process_elements]
            thru_nucs = list(set(inflow.comp.keys()).difference(set(process_nucs)))

            efficiency = [self.calculate_removal_efficiency(elem) for elem in process_elements]
            efficiency = dict(zip(process_elements, efficiency))

            nuc_efficiency = {}
            for nuc in process_nucs:
                elem = re.match(r"([A-Z]+)([0-9]+)", nuc, re.I).groups()[0]
                nuc_efficiency[nuc] = efficiency[elem]

            thru_mass = np.array([inflow.get_mass(nuc) * (1.0 - nuc_efficiency[nuc]) for nuc in process_nucs])
            waste_mass = np.array([inflow.get_mass(nuc) * nuc_efficiency[nuc] for nuc in process_nucs])

            total_waste_mass = np.sum(waste_mass)
            total_thru_mass = inflow.mass - np.sum(waste_mass)

            waste_mass = dict(zip(process_nucs, waste_mass / total_waste_mass))

            thru_mass_1 = np.array([inflow.get_mass(nuc) for nuc in thru_nucs])

            thru_mass_1 = dict(zip(thru_nucs, thru_mass_1 / total_thru_mass))
            thru_mass = dict(zip(process_nucs, thru_mass / total_thru_mass))
            thru_mass.update(thru_mass_1)
        else:
            total_thru_mass = inflow.mass
            thru_mass = inflow.comp.copy()

        waste_stream = Materialflow(comp=waste_mass)
        if bool(waste_mass) and np.max(list(waste_mass.values())) > 0.0:
            waste_stream.volume = total_waste_mass / waste_stream.mass
            waste_stream.mass = total_waste_mass
        else:
            waste_stream.volume = 0.0
        #breakpoint()
        # preserve inflow attributes
        thru_flow = deepcopy(inflow)
        thru_flow.replace_components(thru_mass)
        # initial guess
        thru_flow.volume = inflow.volume - waste_stream.volume
        # correction
        thru_flow.volume = thru_flow.volume * total_thru_mass / thru_flow.get_mass()
        thru_flow.mass = total_thru_mass
        #breakpoint()
        #thru_flow.mass = float(inflow.mass - waste_stream.mass)
        #thru_flow.norm_comp()

        del thru_mass, waste_mass

        return thru_flow, waste_stream
