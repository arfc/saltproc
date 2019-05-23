# import h5py
import silx.io.dictdump as dd
import copy
from pyne import nucname as pyname
import pandas as pd
import numpy as np
import tables as tb
from collections import OrderedDict


class Simulation():
    """ Class setups parameters for simulation, runs SERPENT, parse output,
    create input.
    """

    def __init__(
            self,
            sim_name="default",
            sim_depcode="SERPENT",
            core_number=0,
            db_file="default",
            iter_matfile="default",
            timesteps=0,
            mass_units="kg"):
        """Initializes the class

        Parameters:
        -----------
        sim_name: string
            name of simulation may contain number of reference case, paper name
             or other specific information to identify simulation
        sim_depcode: object
            object of depletiob code initiated using depcode class
        cores: int
            number of cores to use for SERPENT run
        nodes: int
            number of nodes to use for SERPENT run
        bw: string
            # !! if 'True', runs saltproc on Blue Waters
        sss_exec_path: string
            path to SERPENT executable
        restart: bool
            if 'True', restarts simulation using existing HDF5  database
        timesteps: int
            duration of each depletion simulation
        t_0: int
            beggining of simulation moment in time (0 for new run, >0 when
             restarting)
        t_final: int
            duration of whole Saltproc simulation
        input_filename: string
            name of JSON input file with reprocessing scheme and parameters for
             Saltproc simulation
        db_file: string
            name of HDF5 database
        connection_graph: dict
            key: ???
            value: ???
        """
        # initialize all object attributes
        self.sim_name = sim_name
        self.sim_depcode = sim_depcode
        self.core_number = core_number
        self.db_file = db_file
        self.iter_matfile = iter_matfile
        self.timesteps = timesteps
        self.mass_units = mass_units

    def runsim(self):
        """"""
        """for i in range(self.timesteps):
            print ("Step #%i has been started" % (self.timesteps))
            if i == 0:  # First run
                self.sim_depcode.write_depcode_input(
                            self.sim_depcode.template_fname,
                            self.sim_depcode.input_fname)
                self.sim_depcode.run_depcode(self.core_number)
                dep_dict, dep_dict_names = self.sim_depcode.read_bumat(
                                           self.sim_depcode.input_fname,
                                           self.mass_units,
                                           0)
                # Initialize dictionary, HDF5 with cumulative data for all step
                self.init_db(self.db_file)
                cum_dict_h5 = copy.deepcopy(dep_dict_names)  # store init comp
            else:
                self.sim_depcode.run_depcode(self.core_number)
            dep_dict, dep_dict_names = self.sim_depcode.read_bumat(
                                       self.sim_depcode.input_fname,
                                       self.mass_units,
                                       1)
            cum_dict_h5 = self.add_adens_to_dict(cum_dict_h5,
                                                 dep_dict_names)
            self.sim_depcode.read_sim_param()
            # print(self.sim_depcode.keff)
            self.write_db(cum_dict_h5, self.db_file, i+1)
            self.sim_depcode.write_mat_file(dep_dict, self.iter_matfile, i)"""
#############################################################################
        self.sim_depcode.read_sim_param()  # read simulation parameters
        mats = self.sim_depcode.read_dep_comp(self.sim_depcode.input_fname,
                                              self.mass_units,
                                              1)
        # print(materials['ctrlPois']['O16'])
        # print(fuel_salt.comp.keys())
        # print(fuel_salt.comp[962470000])
        print(mats['fuel'])
        print(mats['fuel'].temp)
        print(mats['fuel'].mass_flowrate)
        print(mats['fuel'].mass)
#############################################################################
        self.hdf5store(self.db_file, mats)

        # self.sim_depcode.write_mat_file(materials, self.iter_matfile, 1)

        # self.sim_depcode.get_tra_or_dec()
        # for key, value in self.sim_depcode.iso_map.items():
        #     if '95242.09c' in value:
        #         print(key, self.sim_depcode.iso_map[key])
        # print(self.sim_depcode.iso_map[952420])
        # print(self.sim_depcode.iso_map[471101])
        # print(self.sim_depcode.iso_map[521291])
        # print(self.sim_depcode.iso_map)
        # print(len(self.sim_depcode.iso_map))
        # print(self.sim_depcode.iso_map[471101])
        # print(self.sim_depcode.dec_iso)
        # fuel_salt.write_text('fuel_write_text.txt')
        # fuel_salt.write_json('fuel_write.json')
        # dep_dict, dep_dict_names = self.sim_depcode.read_bumat(
        #                            self.sim_depcode.input_fname,
        #                            self.mass_units,
        #                            0)
        # dep_dict, dep_dict_names = self.sim_depcode.read_bumat(
        #                            self.sim_depcode.input_fname, 1)
        # print (cum_dict_h5)
        # self.init_db(self.db_file)
        # self.write_db(cum_dict_h5, self.db_file, 1)

    def steptime(self):
        return

    def loadinput_sp(self):
        return

    def hdf5store(self, h5_file, mats):
        """ Initializes HDF5 database (if not exist) or append depletion
            step data to it.
        """
        # Moment when store compositions
        moment = 'before_reproc'
        # Retrieving user setting for mass units, converting and append
        mass_convert_factor = self.get_mass_units(self.mass_units)
        # Define compression
        filters = tb.Filters(complevel=9, complib='blosc', fletcher32=True)
        iso_idx = OrderedDict()
        # numpy array row storage data for material physical properties
        mpar_dtype = np.dtype([
                        ('mass',            float),
                        ('density',         float),
                        ('volume',          float),
                        ('temperature',      float),
                        ('mass_flowrate',   float),
                        ('void_fraction',   float),
                        ('burnup',          float)
                        ])

        db = tb.open_file(h5_file,
                          mode='a')
        if not hasattr(db.root, 'materials'):
            comp_group = db.create_group('/',
                                         'materials',
                                         'Material data')
        # Iterate over all materials
        for key, value in mats.items():
            iso_idx[key] = {}
            iso_wt_frac = []
            coun = 0
            # Create group for each material
            if not hasattr(db.root.materials, key):
                m_group = db.create_group(comp_group,
                                          key)
            # Create group for composition and parameters before reprocessing
            # if not hasattr(db.root.materials, key + '/' + moment):
            mat_node = getattr(db.root.materials, key)
            if not hasattr(mat_node, moment):
                before_group = db.create_group(
                                    m_group,
                                    moment,
                                    'Material data before reprocessing')
            comp_pfx = '/materials/' + str(key) + '/' + str(moment)
            # Read isotopes from Materialflow for material
            for nuc_code, wt_frac in mats[key].comp.items():
                # Dictonary in format {isotope_name : index(int)}
                iso_idx[key][self.sim_depcode.get_nuc_name(nuc_code)[0]] = coun
                # Convert wt% to absolute [user units]
                iso_wt_frac.append(mass_convert_factor*wt_frac*mats[key].mass)
                coun += 1
                # Store information about material properties in new array row
                mpar_row = (
                            mats[key].mass * mass_convert_factor,
                            mats[key].density,
                            mats[key].vol,
                            mats[key].temp,
                            mats[key].mass_flowrate * mass_convert_factor,
                            mats[key].void_frac,
                            mats[key].burnup
                            )
                mpar_array = np.array([mpar_row], dtype=mpar_dtype)
            # Try to open EArray and table and if not exist - create new one
            try:
                earr = db.get_node(comp_pfx, 'comp')
                print('\n' + str(earr.title) + ' array exist, grabbing data.')
                mpar_table = db.get_node(comp_pfx, 'parameters')
            except Exception:
                print('\nMaterial '+key+' array is not exist, making new one.')
                earr = db.create_earray(
                                comp_pfx,
                                'comp',
                                atom=tb.Float64Atom(),
                                shape=(0, len(iso_idx[key])),
                                title="Isotopic composition for %s" % key,
                                filters=filters)
                # Save isotope indexes map and units in EArray attributes
                earr.flavor = 'python'
                earr._v_attrs.iso_map = iso_idx[key]
                earr._v_attrs.mass_units = self.mass_units
                # Create table for material Parameters
                print('Creating '+key+' parameters table.')
                mpar_table = db.create_table(
                                comp_pfx,
                                'parameters',
                                np.empty(0, dtype=mpar_dtype),
                                "Material parameters data")
            print('Dumping Material %s data %s to %s.' %
                  (key, moment, str(h5_file)))
            # Add row for the timestep to EArray and Material Parameters table
            earr.append(np.array([iso_wt_frac], dtype=np.float64))
            mpar_table.append(mpar_array)
            del (iso_wt_frac)
            del (mpar_array)
        db.close()

    def get_mass_units(self, units):
        """ Returns multiplicator to convert mass to different mass_units
        """
        if units is "g":
            mul_m = 1.
        elif units is "kg":
            mul_m = 1.E-3
        elif units is "t" or "ton" or "tonne" or "MT":
            mul_m = 1.E-6
        else:
            raise ValueError(
                          'Mass units does not supported or does not defined')
        return mul_m
