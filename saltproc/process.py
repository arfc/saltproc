from saltproc import Materialflow
from pyne import nucname as pyname
import numpy as np
import copy
import json
import gc


class Process():
    """ Class describes process which must be applied to Materialflow to change
     composition, direction, etc.
     """

    def __init__(
                self,
                mass_flowrate,
                capacity,
                volume,
                # inflow,
                # outflow,
                # waste_stream_name,
                efficiency,
                # rem_iso
                ):
        """ Initializes the class

        Parameters:
        -----------
        mass_flowrate: float
            mass flow rate of the material flow (g/s)
        capacity: float
            maximum mass flow rate of the material flow which current
             process can handle (g/s)
        volume: float
            total volume of the current facility (cm**3)
        inflow: Materialflow object
            array with isotope vectors from other processes and/or reactor
             with mass moving into the current process (g)
        outflow: Materialflow object
            array with isotope vectors from other processes and/or reactor
             with mass moving from the current procces back to the core (g)/s?
        waste_stream: Materialflow object
            array with isotope vectors from other processes and/or reactor
             with mass moving from the current procces to waste stream (g)/s?
        efficiency: dict
                    key: element name for removal (not isotope)
                    value: removal efficency for the isotope (weight fraction)
        """
        # initialize all object attributes
        self.mass_flowrate = mass_flowrate
        self.capacity = capacity
        self.volume = volume
        # self.inflow = inflow
        # self.outflow = outflow
        # self.waste_stream_name = waste_stream_name
        self.efficiency = efficiency

    # @profile
    def rem_elements(self, inflow):
        """ Returns PyNE material after removal target isotopes from inflow
         with specified efficiency and waste stream PyNE material
        """
        waste_nucvec = {}
        out_nucvec = {}
        # print("Flow Before reprocessing ^^^^\n\n", inflow.print_attr())
        # print("\n\nXe concentration in inflow before % f g" % inflow['Xe136'])
        for iso in inflow.comp.keys():
            el_name = pyname.serpent(iso).split('-')[0]
            if el_name in self.efficiency:
                out_nucvec[iso] = \
                    float(inflow.comp[iso]) * \
                    float(1.0 - self.efficiency[el_name])
                waste_nucvec[iso] = \
                    float(inflow[iso]) * float(self.efficiency[el_name])
                # print(el_name, iso, inflow[iso], waste_nucvec[iso],
                #       self.efficiency[el_name])
            else:
                out_nucvec[iso] = float(inflow.comp[iso])
                waste_nucvec[iso] = 0.0  # zeroes everywhere else
        waste = Materialflow(waste_nucvec)
        inflow.mass = float(inflow.mass - waste.mass)
        inflow.comp = out_nucvec
        inflow.norm_comp()
        # Recalculate volume too (assumed constant density)
        # inflow.vol = float(inflow.mass * inflow.density)
        # outflow.copy_pymat_attrs(inflow)  # Copy additional PyNE attributes
        # print(waste.print_attr())
        """print("Waste class %s and mass %f g " % (waste.__class__, waste.mass))
        print("Outflow class ", outflow.__class__)
        print("Mass ", outflow.mass, inflow.mass, outflow.mass - inflow.mass)
        print("Density ", outflow.density, inflow.density)
        print("atoms_per_molecule ", outflow.atoms_per_molecule == inflow.atoms_per_molecule)
        print("Volume  ", outflow.vol == inflow.vol)
        print("Burnup ", outflow.burnup == inflow.burnup)
        print("Metadata ", outflow.metadata, inflow.metadata)"""
        # print("Flow After reprocessing ^^^^\n\n", inflow.print_attr())
        """print("Xe concentration in inflow after %f g" % inflow['Xe136'])
        print("Waste mass %f g" % waste.mass)"""
        del out_nucvec, waste_nucvec, el_name
        return waste

    def check_mass_conservation(self):
        """ Checking that (outflow + waste_stream) == inflow
        """
        out_stream = self.outflow + self.waste_stream
        np.testing.assert_array_equal(out_stream, self.inflow)
