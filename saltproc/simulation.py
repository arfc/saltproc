import numpy as np
import tables as tb
import os
from collections import OrderedDict


class Simulation():
    """Class for handling simulation information. Contains information
    for running simulation wiht parallelism. Also contains the simulation
    name, a `Depcode` object, and the filename for the simulation database.
    Contains methods to store simulation metadata and depletion results in
    a database, predict reactor criticality at next depletion step, and
    switch simulation geometry.

    """

    def __init__(
            self,
            sim_name="default",
            sim_depcode="depcode",
            core_number=1,
            node_number=1,
            db_path="db_saltproc.h5",
            compression_params=tb.Filters(complevel=9,
                                   complib='blosc',
                                   fletcher32=True),
            iter_matfile="./saltproc_mat"):
        """Initializes the Simulation object.

        Parameters
        ----------
        sim_name : str
            Name to identify the simulation. May contain information such as
            the number of a reference case, a paper name, or some other
            specific information identify the simulation.
        sim_depcode : Depcode object
            An instance of one of the `Depcode` child classes
        cores : int
            Number of cores to use for depletion code run (`-omp` flag in
            Serpent).
        nodes : int
            Number of nodes to use for depletion code run (`-mpi` flag in
            Serpent).
        db_path : str
            Path of HDF5 database that stores simulation information and
            data.
        compression_params : Pytables filter object
            Compression parameters for HDF5 database.
        iter_matfile : str
            Name of iterative, rewritable material file for depletion code
            rerunning. This file is modified during  the simulation.

        """
        # initialize all object attributes
        self.sim_name = sim_name
        self.sim_depcode = sim_depcode
        self.core_number = core_number
        self.node_number = node_number
        self.db_path = db_path
        self.compression_params = compression_params
        self.iter_matfile = iter_matfile

    def runsim_no_reproc(self, reactor, nsteps):
        """Run simulation sequence for integration test. No reprocessing
        involved, just re-running depletion code for comparision with model
        output.

        Parameters
        ----------
        reactor : Reactor object
            Contains information about power load curve and cumulative
            depletion time for the integration test.
        nsteps : int
            Number of depletion time steps in integration test run.

        """

        ######################################################################
        # Start sequence
        for dts in range(nsteps):
            print("\nStep #%i has been started" % (dts + 1))
            if dts == 0:  # First step
                self.sim_depcode.write_depcode_input(
                    self.sim_depcode.template_path,
                    self.sim_depcode.input_path,
                    reactor,
                    dts,
                    False)
                self.sim_depcode.run_depcode(
                    self.core_number,
                    self.node_number)
                # Read general simulation data which never changes
                self.store_run_init_info()
                # Parse and store data for initial state (beginning of dts)
                mats = self.sim_depcode.read_dep_comp(
                    self.sim_depcode.input_path,
                    False)
                self.store_mat_data(mats, dts, 'before_reproc')
            # Finish of First step
            # Main sequence
            else:
                self.sim_depcode.run_depcode(
                    self.core_number,
                    self.node_number)
            mats = self.sim_depcode.read_dep_comp(
                self.sim_depcode.input_path,
                True)
            self.store_mat_data(mats, dts, 'before_reproc')
            self.store_run_step_info()
            self.sim_depcode.write_mat_file(
                mats,
                self.iter_matfile,
                self.burn_time)

    def store_after_repr(self, after_mats, waste_dict, step):
        """Adds to HDF5 database waste streams data for each process after
        reprocessing was performed (grams per depletion step).

        Parameters
        ----------
        after_mats : `Materialflow`
            Burnable material stream object after performing reprocessing.
        waste_dict : dict of str to Materialflow
            Dictionary that maps `Process` objects to waste `Materialflow`
            objects.

            ``key``
                `Process` name (`str`)
            ``value``
                `Materialflow` object containing waste streams data.
        step : int
            Current depletion step.

        """
        streams_gr = 'in_out_streams'
        db = tb.open_file(self.db_path, mode='a', filters=self.compression_params)
        for mn in waste_dict.keys():  # iterate over materials
            mat_node = getattr(db.root.materials, mn)
            if not hasattr(mat_node, streams_gr):
                waste_group = db.create_group(
                    mat_node,
                    streams_gr,
                    'Waste Material streams data for each process')
            else:
                waste_group = getattr(mat_node, streams_gr)
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
                    iso_wt_frac.append(wt_frac * waste_dict[mn][proc].mass)
                    coun += 1
                # Try to open EArray and table and if not exist - create
                try:
                    earr = db.get_node(waste_group, proc)
                except Exception:
                    earr = db.create_earray(
                        waste_group,
                        proc,
                        atom=tb.Float64Atom(),
                        shape=(0, len(iso_idx)),
                        title="Isotopic composition for %s" % proc)
                    # Save isotope indexes map and units in EArray attributes
                    earr.flavor = 'python'
                    earr.attrs.iso_map = iso_idx
                earr.append(np.asarray([iso_wt_frac], dtype=np.float64))
                del iso_wt_frac
                del iso_idx
        # Also save materials AFTER reprocessing and refill here
        self.store_mat_data(after_mats, step, 'after_reproc')
        db.close()

    def store_mat_data(self, mats, d_step, moment):
        """Initializes HDF5/Pytables database (if not exist) or append burnable
        material composition, mass, density, volume, temperature, burnup,
        mass_flowrate, void_fraction, at the current depletion step to it.

        Parameters
        ----------
        mats : dict of str to Materialflow
            Dictionary that contains `Materialflow` objects.

            ``key``
                Name of burnable material.
            ``value``
                `Materialflow` object holding composition and properties.
        d_step : int
            Current depletion step.
        moment : int
            Indicates at which moment in the depletion step store the data. `0`
            refers the beginning, `1` refers the end of depletion step.

        """
        # Moment when store compositions
        iso_idx = OrderedDict()
        # numpy array row storage data for material physical properties
        mpar_dtype = np.dtype([
            ('mass', float),
            ('density', float),
            ('volume', float),
            ('temperature', float),
            ('mass_flowrate', float),
            ('void_fraction', float),
            ('burnup', float)
        ])

        print('\nStoring material data for depletion step #%i.' % (d_step + 1))
        db = tb.open_file(self.db_path, mode='a', filters=self.compression_params)
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
                db.create_group(comp_group,
                                key)
            # Create group for composition and parameters before reprocessing
            mat_node = getattr(db.root.materials, key)
            if not hasattr(mat_node, moment):
                db.create_group(mat_node,
                                moment,
                                'Material data before reprocessing')
            comp_pfx = '/materials/' + str(key) + '/' + str(moment)
            # Read isotopes from Materialflow for material
            for nuc_code, wt_frac in mats[key].comp.items():
                # Dictonary in format {isotope_name : index(int)}
                iso_idx[key][self.sim_depcode.get_nuc_name(nuc_code)[0]] = coun
                # Convert wt% to absolute [user units]
                iso_wt_frac.append(wt_frac * mats[key].mass)
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
                print(
                    'Material ' +
                    key +
                    ' array is not exist, making new one.')
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
                print('Creating ' + key + ' parameters table.')
                mpar_table = db.create_table(
                    comp_pfx,
                    'parameters',
                    np.empty(0, dtype=mpar_dtype),
                    "Material parameters data")
            print('Dumping Material %s data %s to %s.' %
                  (key, moment, os.path.abspath(self.db_path)))
            # Add row for the timestep to EArray and Material Parameters table
            earr.append(np.array([iso_wt_frac], dtype=np.float64))
            mpar_table.append(mpar_array)
            del (iso_wt_frac)
            del (mpar_array)
            mpar_table.flush()
        db.close()

    def store_run_step_info(self):
        """Adds to database Serpent and Saltproc simulation parameters
        (execution time, memory usage), multiplication factor, breeding ratio,
        delayed neutron precursor data, fission mass, cumulative depletion
        time, power level for the current time step.
        """

        # Read info from depcode _res.m File
        self.sim_depcode.read_depcode_step_param()
        # Initialize beta groups number
        b_g = len(self.sim_depcode.param['beta_eff'])
        # numpy array row storage for run info

        class Step_info(tb.IsDescription):
            keff_bds = tb.Float32Col((2,))
            keff_eds = tb.Float32Col((2,))
            breeding_ratio = tb.Float32Col((2,))
            step_execution_time = tb.Float32Col()
            cumulative_time_at_eds = tb.Float32Col()
            power_level = tb.Float32Col()
            memory_usage = tb.Float32Col()
            beta_eff_eds = tb.Float32Col((b_g, 2))
            delayed_neutrons_lambda_eds = tb.Float32Col((b_g, 2))
            fission_mass_bds = tb.Float32Col()
            fission_mass_eds = tb.Float32Col()
        # Open or restore db and append data to it
        db = tb.open_file(self.db_path, mode='a', filters=self.compression_params)
        try:
            step_info_table = db.get_node(
                db.root,
                'simulation_parameters')
            # Read burn_time from previous step
            self.burn_time = step_info_table.col('cumulative_time_at_eds')[-1]
        except Exception:
            step_info_table = db.create_table(
                db.root,
                'simulation_parameters',
                Step_info,
                "Simulation parameters after each timestep")
            # Intializing burn_time array at the first depletion step
            self.burn_time = 0.0
        self.burn_time += self.sim_depcode.param['burn_days']
        # Define row of table as step_info
        step_info = step_info_table.row
        # Define all values in the row
        step_info['keff_bds'] = self.sim_depcode.param['keff_bds']
        step_info['keff_eds'] = self.sim_depcode.param['keff_eds']
        step_info['breeding_ratio'] = self.sim_depcode.param[
            'breeding_ratio']
        step_info['step_execution_time'] = self.sim_depcode.param[
            'execution_time']
        step_info['cumulative_time_at_eds'] = self.burn_time
        step_info['power_level'] = self.sim_depcode.param['power_level']
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
        """Adds to database Serpent and Saltproc simulation parameters before
        starting depletion sequence.
        """
        # numpy arraw row storage for run info
        sim_info_dtype = np.dtype([
            ('neutron_population', int),
            ('active_cycles', int),
            ('inactive_cycles', int),
            ('serpent_version', 'S20'),
            ('title', 'S90'),
            ('serpent_input_filename', 'S90'),
            ('serpent_working_dir', 'S90'),
            ('xs_data_path', 'S90'),
            ('OMP_threads', int),
            ('MPI_tasks', int),
            ('memory_optimization_mode', int),
            ('depletion_timestep', float)
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
            self.sim_depcode.sim_info['memory_optimization_mode'],
            self.sim_depcode.sim_info['depletion_timestep']
        )
        sim_info_array = np.array([sim_info_row], dtype=sim_info_dtype)
        # Open or restore db and append datat to it
        db = tb.open_file(self.db_path, mode='a', filters=self.compression_params)
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

    def switch_to_next_geometry(self):
        """Inserts line with path to next Serpent geometry file at the
        beginning of the Serpent iteration input file.
        """
        geo_line_n = 5
        f = open(self.sim_depcode.input_path, 'r')
        data = f.readlines()
        f.close()

        current_geo_file = data[geo_line_n].split('\"')[1]
        current_geo_idx = self.sim_depcode.geo_file.index(current_geo_file)
        try:
            new_geo_file = self.sim_depcode.geo_file[current_geo_idx + 1]
        except IndexError:
            print('No more geometry files available \
                  and the system went subcritical \n\n')
            print('Simulation ended')
            return
        new_data = [d.replace(current_geo_file, new_geo_file) for d in data]
        print('Switching to next geometry file: ', new_geo_file)

        f = open(self.sim_depcode.input_path, 'w')
        f.writelines(new_data)
        f.close()

    def read_k_eds_delta(self, current_timestep, restart):
        """Reads from database delta between previous and current `keff` at the
        end of depletion step and returns `True` if predicted `keff` at the
        next depletion step drops below 1.

        Parameters
        ----------
        current_timestep : int
            Number of current depletion time step.
        restart : bool
            Was this simulation restarted?

        Returns
        -------
        bool
            Is the reactor will become subcritical at the next step?

        """

        if current_timestep > 3 or restart:
            # Open or restore db and read data
            db = tb.open_file(self.db_path, mode='r')
            sim_param = db.root.simulation_parameters
            k_eds = np.array([x['keff_eds'][0] for x in sim_param.iterrows()])
            db.close()
            delta_keff = np.diff(k_eds)
            avrg_keff_drop = abs(np.mean(delta_keff[-4:-1]))
            print("Average keff drop per step ", avrg_keff_drop)
            print("keff at the end of last step ", k_eds)
            if k_eds[-1] - avrg_keff_drop < 1.0:
                return True
            else:
                return False

    def check_switch_geo_trigger(self, current_time, switch_time):
        """Compares current timestep with user defined time to switch geometry.
        Returns `True` if its time.

        Parameters
        ----------
        current_timestep : int
            Current time after depletion started.
        switch_time : list
            List containing moments in time when geometry have to be switched.

        Returns
        -------
        bool
            is the next geometry must be used at the next step?

        """
        if current_time in switch_time:
            return True
        else:
            return False
