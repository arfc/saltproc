# import h5py
import silx.io.dictdump as dd


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
            iter_matfile):
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
        timestep: int
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

    def runsim(self):
        # self.sim_depcode.write_depcode_input(self.sim_depcode.template_fname,
        #                                      self.sim_depcode.input_fname)
        # self.sim_depcode.run_depcode(self.core_number)
        # self.sim_depcode.read_bumat(self.sim_depcode.input_fname,
        #                            0)
        dep_dict, dep_dict_h = self.sim_depcode.read_bumat(self.sim_depcode.
                                                           input_fname,
                                                           0)
        # self.sim_depcode.write_mat_file(depletion_dict, self.iter_matfile)
        # print (dep_dict_h)
        # self.init_db(self.db_file)
        self.write_db(dep_dict_h, self.db_file)

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
                    overwrite_data=False,
                    create_dataset_args={'compression': "gzip",
                                         'shuffle': True,
                                         'fletcher32': True})
        # dd.io.save(hdf5_db_file, depletion)
        # dictToH5(hdf5_db_file, depletion)

    def reopen_db(self):
        return

    def write_db(self, depletion, hdf5_db_file):
        """ Dump dictionary with depletion data in HDF5 database
        """
        dd.dicttoh5(depletion,
                    hdf5_db_file,
                    mode='a',
                    overwrite_data=True,
                    create_dataset_args={'compression': "gzip",
                                         'shuffle': True,
                                         'fletcher32': True})
        print ("\nData for depletion step # have been saved\n")
