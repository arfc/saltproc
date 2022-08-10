"""Process module"""
#from math import *
import numpy as np

from pyne import nucname as pyname
from saltproc import Materialflow


class Process():
    """Represents an aribtrary processing component that extracts nuclides from
    a material.
     """

    def __init__(self, *initial_data, **kwargs):
        """ Initializes the Process object.

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
        waste_nucvec = {}
        thru_nucvec = {}
        print("Xe concentration in inflow before % f g" % inflow['Xe136'])
        print("Current time %f" % (t))

        for nuc in inflow.comp.keys():
            nuc_name = pyname.serpent(nuc).split('-')[0]
            if nuc_name in self.efficiency:
                # Evaluate removal efficiency for nuc_name (float)
                self.efficiency[nuc_name] = \
                    self.calculate_removal_efficiency(nuc_name)

                thru_nucvec[nuc] = \
                    float(inflow.comp[nuc]) * \
                    float(1.0 - self.efficiency[nuc_name])

                waste_nucvec[nuc] = \
                    float(inflow[nuc]) * self.efficiency[nuc_name]

            # Assume zero removal
            else:
                thru_nucvec[nuc] = float(inflow.comp[nuc])
                waste_nucvec[nuc] = 0.0

        waste_stream = Materialflow(waste_nucvec)
        thru_flow = Materialflow(thru_nucvec)
        thru_flow.mass = float(inflow.mass - waste_stream.mass)
        thru_flow.norm_comp()

        print("Xe concentration in thruflow: %f g" % thru_flow['Xe136'])
        print("Waste mass: %f g\n" % waste_stream.mass)

        del thru_nucvec, waste_nucvec, nuc_name

        return thru_flow, waste_stream
