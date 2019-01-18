# import h5py
import silx.io.dictdump as dd
import copy


class Simulation():
    """ Class setups parameters for simulation, runs SERPENT, parse output,
    create input.
    """

    def __init__(
            self,
            sim_name,
            sim_depcode,
            core_number,
            db_file,
            iter_matfile,
            timesteps):
        """ Initializes the class

        Parameters:
        -----------
        sim_name: string
            name of simulation may contain number of reference case, paper name
             or other specific information to identify simulation
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

    def runsim(self):
        for i in range(self.timesteps):
            print ("Step #%i has been started" % (self.timesteps))
            if i == 0:  # First run
                self.sim_depcode.write_depcode_input(
                            self.sim_depcode.template_fname,
                            self.sim_depcode.input_fname)
                self.sim_depcode.run_depcode(self.core_number)
                dep_dict, dep_dict_names = self.sim_depcode.read_bumat(
                                           self.sim_depcode.input_fname, 0)
                # Initialize dictionary, HDF5 with cumulative data for all step
                self.init_db(self.db_file)
                cum_dict_h5 = copy.deepcopy(dep_dict_names)  # store init comp
            else:
                self.sim_depcode.run_depcode(self.core_number)
            dep_dict, dep_dict_names = self.sim_depcode.read_bumat(
                                       self.sim_depcode.input_fname, 1)
            cum_dict_h5 = self.add_adens_to_dict(cum_dict_h5,
                                                 dep_dict_names)
            self.sim_depcode.read_out()
            print(self.sim_depcode.keff)
            self.write_db(cum_dict_h5, self.db_file, i+1)
            self.sim_depcode.write_mat_file(dep_dict, self.iter_matfile, i)
        # dep_dict, dep_dict_names = self.sim_depcode.read_bumat(
        #                            self.sim_depcode.input_fname, 0)
        # dep_dict, dep_dict_names = self.sim_depcode.read_bumat(
        #                            self.sim_depcode.input_fname, 1)
        # print (cum_dict_h5)
        # self.init_db(self.db_file)
        # self.write_db(cum_dict_h5, self.db_file, 1)

    def steptime(self):
        return

    def loadinput_sp(self):
        return

    def init_db(self, hdf5_db_file):
        """ Initializes the database and save it """
        simulation_parameters = {
            "Transport_code": self.sim_depcode.codename,
            "Simulation_name": self.sim_name,
            "Number_of_cores": self.core_number,
            "Neutron_population": self.sim_depcode.npop,
            "Active_cycles": self.sim_depcode.active_cycles,
            "Inactive_cycles": self.sim_depcode.inactive_cycles
        }
        # print (simulation_parameters)
        dd.dicttoh5(simulation_parameters, hdf5_db_file,
                    mode='w',
                    overwrite_data=True,
                    create_dataset_args={'compression': "gzip",
                                         'shuffle': True,
                                         'fletcher32': True})
        # dd.io.save(hdf5_db_file, depletion)
        # dictToH5(hdf5_db_file, depletion)

    def reopen_db(self):
        return

    def write_db(self, depletion, hdf5_db_file, step):
        """ Dump dictionary with depletion data in HDF5 database
        """
        dset_args = {'compression': "gzip",
                     'shuffle': True,
                     'fletcher32': True}
        dd.dicttoh5(depletion,
                    hdf5_db_file,
                    mode='a',
                    overwrite_data=True,
                    create_dataset_args=dset_args)
        dd.dicttoh5(self.sim_depcode.keff,
                    hdf5_db_file,
                    mode='a',
                    overwrite_data=True,
                    create_dataset_args=dset_args)
        print ("\nData for depletion step #%i have been saved\n" % (step))

    def add_adens_to_dict(self, cum_depletion, depletion):
        """ Adds atomic densities for current step to existing dictionary to
            make it possible to store in HDF5.
        """
        for key, value in cum_depletion.items():
            for nname, adens in cum_depletion[key]['nuclides'].items():
                adens = depletion[key]['nuclides'][nname][0]
                cum_depletion[key]['nuclides'][nname].append(float(adens))
        return cum_depletion
