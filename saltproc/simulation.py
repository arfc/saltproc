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
            h5_file="db_saltproc.h5",
            compression=None,
            iter_matfile="default",
            timesteps=0):
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
        h5_file: string
            name of HDF5 database
        compression: Pytables filter object
            HDF5 fatabase compression parameters
        connection_graph: dict
            key: ???
            value: ???
        """
        # initialize all object attributes
        self.sim_name = sim_name
        self.sim_depcode = sim_depcode
        self.core_number = core_number
        self.h5_file = h5_file
        self.compression = compression
        self.iter_matfile = iter_matfile
        self.timesteps = timesteps

    def runsim_no_reproc(self):
        """ Run simulation sequence """
        ######################################################################
        # Start sequence
        for dts in range(self.timesteps):
            print ("\nStep #%i has been started" % (dts+1))
            if dts == 0:  # First step
                self.sim_depcode.write_depcode_input(
                                    self.sim_depcode.template_fname,
                                    self.sim_depcode.input_fname)
                self.sim_depcode.run_depcode(self.core_number)
                # Read general simulation data which never changes
                self.store_run_init_info()
                # Parse and store data for initial state (beginning of dts)
                mats = self.sim_depcode.read_dep_comp(
                                            self.sim_depcode.input_fname,
                                            0)
                self.store_mat_data(mats, dts, 'before_reproc')
            # Finish of First step
            # Main sequence
            else:
                self.sim_depcode.run_depcode(self.core_number)
            mats = self.sim_depcode.read_dep_comp(
                                              self.sim_depcode.input_fname,
                                              1)
            self.store_mat_data(mats, dts, 'before_reproc')
            self.store_run_step_info()
            self.sim_depcode.write_mat_file(mats, self.iter_matfile, dts)
##############################################################################
        # self.sim_depcode.write_depcode_input(
        #                     self.sim_depcode.template_fname,
        #                     self.sim_depcode.input_fname)
        # self.sim_depcode.run_depcode(self.core_number)
        # mats = self.sim_depcode.read_dep_comp(self.sim_depcode.input_fname,0)
        # print(len(self.sim_depcode.iso_map))
        # print (len(mats['fuel'].comp))
        # print (len(mats['ctrlPois'].comp))
        # self.store_mat_data(mats, 111)
        # self.sim_depcode.write_mat_file(mats, self.iter_matfile, 1)
#############################################################################
        # self.store_mat_data(mats)

        # self.sim_depcode.get_tra_or_dec()

        # self.store_run_step_info()
        # self.store_mat_data(mats)

        # self.mat_comp_preprosessor()

    def steptime(self):
        return 1

    def loadinput_sp(self):
        return

    def store_waste_data(self, a_mat, waste_dict, step):
        """ Adds to HDF5 database waste streams data for each process (g/step).
        """
        db = tb.open_file(self.h5_file, mode='a', filters=self.compression)
        for mn in waste_dict.keys():  # iterate over materials
            mat_node = getattr(db.root.materials, mn)
            if not hasattr(mat_node, 'waste_streams'):
                waste_group = db.create_group(
                                mat_node,
                                'waste_streams',
                                'Waste Material streams data for each process')
            for proc in waste_dict[mn].keys():
                # proc_node = db.create_group(waste_group, proc)
                # iso_idx[proc] = OrderedDict()
                iso_idx = OrderedDict()
                iso_wt_frac = []
                coun = 0
                # Read isotopes from Materialflow
                for nuc, wt_frac in waste_dict[mn][proc].comp.items():
                    # Dictonary in format {isotope_name : index(int)}
                    iso_idx[self.sim_depcode.get_nuc_name(nuc)[0]] = coun
                    # Convert wt% to absolute [user units]
                    iso_wt_frac.append(wt_frac*waste_dict[mn][proc].mass)
                    coun += 1
                # Try to open EArray and table and if not exist - create
                try:
                    earr = db.get_node(waste_group, proc)
                except Exception:
                    print("Size of list: ", len(iso_idx), coun, mn, proc)
                    earr = db.create_earray(
                                    waste_group,
                                    proc,
                                    atom=tb.Float64Atom(),
                                    shape=(0, len(iso_idx)),
                                    title="Isotopic composition for %s" % proc)
                    # Save isotope indexes map and units in EArray attributes
                    earr.flavor = 'python'
                    earr.attrs.iso_map = iso_idx
                earr.append(np.array([iso_wt_frac], dtype=np.float64))
                del iso_wt_frac
                del iso_idx
        db.close()

    def store_mat_data(self, mats, d_step, moment):
        """ Initializes HDF5 database (if not exist) or append depletion
            step data to it.
        """
        # Moment when store compositions
        # moment = 'before_reproc'
        iso_idx = OrderedDict()
        # numpy array row storage data for material physical properties
        mpar_dtype = np.dtype([
                        ('mass',            float),
                        ('density',         float),
                        ('volume',          float),
                        ('temperature',     float),
                        ('mass_flowrate',   float),
                        ('void_fraction',   float),
                        ('burnup',          float)
                        ])

        print('\nStoring material data for depletion step #%i.' % (d_step+1))
        db = tb.open_file(self.h5_file, mode='a', filters=self.compression)
        if not hasattr(db.root, 'materials'):
            comp_group = db.create_group('/',
                                         'materials',
                                         'Material data')
        # Iterate over all materials
        for key, value in mats.items():
            iso_idx[key] = OrderedDict()
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
                                    mat_node,
                                    moment,
                                    'Material data before reprocessing')
            comp_pfx = '/materials/' + str(key) + '/' + str(moment)
            # Read isotopes from Materialflow for material
            for nuc_code, wt_frac in mats[key].comp.items():
                # Dictonary in format {isotope_name : index(int)}
                iso_idx[key][self.sim_depcode.get_nuc_name(nuc_code)[0]] = coun
                # Convert wt% to absolute [user units]
                iso_wt_frac.append(wt_frac*mats[key].mass)
                coun += 1
            # Store information about material properties in new array row
            mpar_row = (
                        mats[key].mass,
                        mats[key].density,
                        mats[key].vol,
                        mats[key].temp,
                        mats[key].mass_flowrate,
                        mats[key].void_frac,
                        mats[key].burnup
                        )
            mpar_array = np.array([mpar_row], dtype=mpar_dtype)
            # Try to open EArray and table and if not exist - create new one
            try:
                earr = db.get_node(comp_pfx, 'comp')
                print(str(earr.title) + ' array exist, appending data.')
                mpar_table = db.get_node(comp_pfx, 'parameters')
            except Exception:
                print('Material '+key+' array is not exist, making new one.')
                earr = db.create_earray(
                                comp_pfx,
                                'comp',
                                atom=tb.Float64Atom(),
                                shape=(0, len(iso_idx[key])),
                                title="Isotopic composition for %s" % key)
                # Save isotope indexes map and units in EArray attributes
                earr.flavor = 'python'
                earr.attrs.iso_map = iso_idx[key]
                # Create table for material Parameters
                print('Creating '+key+' parameters table.')
                mpar_table = db.create_table(
                                comp_pfx,
                                'parameters',
                                np.empty(0, dtype=mpar_dtype),
                                "Material parameters data")
            print('Dumping Material %s data %s to %s.' %
                  (key, moment, str(self.h5_file)))
            # Add row for the timestep to EArray and Material Parameters table
            # print (iso_wt_frac)
            # print (np.array([iso_wt_frac], dtype=np.float64))
            # print (np.array([iso_wt_frac], dtype=np.float64).shape)
            earr.append(np.array([iso_wt_frac], dtype=np.float64))
            mpar_table.append(mpar_array)
            del (iso_wt_frac)
            del (mpar_array)
            mpar_table.flush()
        db.close()

    def store_run_step_info(self):
        """ Write to database important SERPENT and Saltproc run parameters,
            breeding ratio, beta, etc for each timestep
        """
        # numpy arraw row storage for run info
        class Step_info(tb.IsDescription):
            keff_bds = tb.Float32Col((2,))
            keff_eds = tb.Float32Col((2,))
            breeding_ratio = tb.Float32Col((2,))
            step_execution_time = tb.Float32Col()
            memory_usage = tb.Float32Col()
            beta_eff_eds = tb.Float32Col((9, 2))
            delayed_neutrons_lambda_eds = tb.Float32Col((9, 2))
            fission_mass_bds = tb.Float32Col()
            fission_mass_eds = tb.Float32Col()
        # Read info from depcode _res.m File
        self.sim_depcode.read_depcode_step_param()
        # Open or restore db and append datat to it
        db = tb.open_file(self.h5_file, mode='a', filters=self.compression)
        try:
            step_info_table = db.get_node(
                                         db.root,
                                         'simulation_parameters')
        except Exception:
            step_info_table = db.create_table(
                                db.root,
                                'simulation_parameters',
                                Step_info,
                                "Simulation parameters after each timestep")
        # Define row of table as step_info
        step_info = step_info_table.row

        # Define all values in the row
        step_info['keff_bds'] = self.sim_depcode.param['keff_bds']
        step_info['keff_eds'] = self.sim_depcode.param['keff_eds']
        step_info['breeding_ratio'] = self.sim_depcode.param[
                                        'breeding_ratio']
        step_info['step_execution_time'] = self.sim_depcode.param[
                                        'execution_time']
        step_info['memory_usage'] = self.sim_depcode.param[
                                        'memory_usage']
        step_info['beta_eff_eds'] = self.sim_depcode.param[
                                        'beta_eff']
        step_info['delayed_neutrons_lambda_eds'] = self.sim_depcode.param[
                                        'delayed_neutrons_lambda']
        step_info['fission_mass_bds'] = self.sim_depcode.param[
                                        'fission_mass_bds']
        step_info['fission_mass_eds'] = self.sim_depcode.param[
                                        'fission_mass_eds']
        # Inject the Record value into the table
        step_info.append()
        step_info_table.flush()
        db.close()

    def store_run_init_info(self):
        """ Write to database important SERPENT and Saltproc run parameters
            before starting depletion sequence
        """
        # numpy arraw row storage for run info
        sim_info_dtype = np.dtype([
                    ('neutron_population',       int),
                    ('active_cycles',            int),
                    ('inactive_cycles',          int),
                    ('serpent_version',         'S7'),
                    ('title',                  'S50'),
                    ('serpent_input_filename', 'S80'),
                    ('serpent_working_dir',    'S80'),
                    ('xs_data_path',           'S80'),
                    ('OMP_threads',              int),
                    ('MPI_tasks',                int),
                    ('memory_optimization_mode', int)
                    ])
        # Read info from depcode _res.m File
        self.sim_depcode.read_depcode_info()
        # Store information about material properties in new array row
        sim_info_row = (
                    self.sim_depcode.npop,
                    self.sim_depcode.active_cycles,
                    self.sim_depcode.inactive_cycles,
                    self.sim_depcode.sim_info['serpent_version'],
                    self.sim_depcode.sim_info['title'],
                    self.sim_depcode.sim_info['serpent_input_filename'],
                    self.sim_depcode.sim_info['serpent_working_dir'],
                    self.sim_depcode.sim_info['xs_data_path'],
                    self.sim_depcode.sim_info['OMP_threads'],
                    self.sim_depcode.sim_info['MPI_tasks'],
                    self.sim_depcode.sim_info['memory_optimization_mode']
                    )
        # print(sim_info_row)
        sim_info_array = np.array([sim_info_row], dtype=sim_info_dtype)
        # Open or restore db and append datat to it
        db = tb.open_file(self.h5_file, mode='a', filters=self.compression)
        try:
            sim_info_table = db.get_node(db.root, 'initial_depcode_siminfo')
        except Exception:
            sim_info_table = db.create_table(
                                db.root,
                                'initial_depcode_siminfo',
                                sim_info_array,
                                "Initial depletion code simulation parameters")
        sim_info_table.flush()
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

    def mat_comp_preprosessor(self):
        """ Reads Serpent input file with burnable materials and overwrites it
        with full list of isotopes based on short Serpent run.
        """
        print('Prepare files to start Serpent run')
        self.sim_depcode.write_depcode_input(
                             self.sim_depcode.template_fname,
                             self.sim_depcode.input_fname)
        print('Running Serpent to generate list of all isotopes for depletion')
        self.sim_depcode.run_depcode(self.core_number)
        mats = self.sim_depcode.read_dep_comp(self.sim_depcode.input_fname, 0)
        print('Creating new material composition file: %s' % self.iter_matfile)
        self.sim_depcode.write_mat_file(mats, self.iter_matfile, 0)
