import math
import itertools
import subprocess
import os
import numpy as np
import sys
import h5py
import shutil
import argparse
from pyne import serpent
from pyne import nucname
from collections import OrderedDict


class saltproc_two_region:
    """ Class saltproc runs SERPENT and manipulates its input and output files
        to reprocess its material, while storing the SERPENT run results in a
        HDF5 database. This class is for two region flows, with fertile blanket
        and fissile driver. The fissile material from the blanket is separated
        and put into the driver.
    """

    def __init__(self, steps, cores, nodes, bw, exec_path, restart=False,
                 input_file='core', db_file='db_saltproc.hdf5',
                 mat_file='fuel_comp', driver_mat_name='fuel',
                 blanket_mat_name='blank'):
        """ Initializes the class

        Parameters:
        -----------
        steps: int
            total number of steps for this saltproc run
        cores: int
            number of cores to use for this saltproc run
        nodes: int
            number of nodes to use for this saltproc run
        bw: string
            # !! if 'True', runs saltproc on Blue Waters
        exec_path: string
            path of SERPENT executable
        restart: bool
            if true, starts from an existing database
        input_file: string
            name of input file
        db_file: string
            name of output hdf5 file
        mat_file: string
            name of material file connected to input file
        driver_mat_name: string
            name of driver material in the definition
        blanket_mat_name: string
            name of blanket material in definition
        """
        # initialize all object attributes
        self.steps = steps
        self.cores = cores
        self.nodes = nodes
        self.bw = bw
        self.exec_path = exec_path
        self.restart = restart
        self.input_file = input_file
        self.db_file = db_file
        self.mat_file = mat_file
        self.current_step = 0
        self.blanket_mat_name = blanket_mat_name
        self.driver_mat_name = driver_mat_name

    def find_iso_indx(self, keyword):
        """ Returns index number of keword in bumat dictionary
        
        Parameters:
        -----------
        keyword: string or list
            keyword to search for - element (e.g. Xe) or isotope (e.g. Pa233)
        
        Returns:
        --------
        numpy array of indices
        """
        indx = 0
        indx_list = []
        if isinstance(keyword, str):
            for key in self.bumat_dict.keys():
                if keyword in key:
                    indx_list.append(indx)
                indx += 1
        elif isinstance(keyword, list):
            for key in self.bumat_dict.keys():
                for keywor in keyword:
                    if keywor in key:
                        indx_list.append(indx)
                indx += 1

        return np.array(indx_list)

    def init_db(self):
        """ Initializes the database from the output of the first
            SEPRENT run """

        self.f = h5py.File(self.db_file, 'w')
        # put in values from initial condition
        bumat_dict, mat_def_dict = self.read_bumat(0)

        # initialize isotope library and number of isotopes
        self.isolib = []
        for key in self.bumat_dict[self.driver_mat_name].keys():
            # needs to incode to put string in h5py
            self.isolib.append(key.encode('utf8'))

        self.number_of_isotopes = len(self.isolib)

        shape = (2, self.steps)
        maxshape = (2, None)
        self.keff_db = self.f.create_dataset('keff_EOC', shape,
                                             maxshape=maxshape, chunks=True)
        self.keff_db_0 = self.f.create_dataset('keff_BOC', shape,
                                               maxshape=maxshape, chunks=True)

        shape = (self.steps + 1, self.number_of_isotopes)
        maxshape = (None, self.number_of_isotopes)
        self.driver_adens_0 = self.f.create_dataset('driver adensity before reproc',
                                                   shape, maxshape=maxshape,
                                                   chunks=True)
        self.driver_adens_1 = self.f.create_dataset('driver adensity after reproc',
                                                   shape, maxshape=maxshape,
                                                   chunks=True)
        self.blanket_adens_0 = self.f.create_dataset('blanket adenstiy before reproc',
                                                     shape, maxshape=maxshape,
                                                     chunks=True)
        self.blanket_adens_1 = self.f.create_dataset('blanket adensity after reproc',
                                                     shape, maxshape=maxshape,
                                                     chunks=True)
        self.tank_adens_db = self.f.create_dataset('tank adensity',
                                                   shape, maxshape=maxshape,
                                                   chunks=True)
        self.refill_tank_db = self.f.create_dataset('refill tank adensity',
                                                 shape, maxshape=maxshape,
                                                 chunks=True)
        # !! raffinate stream consider splitting by what element
        self.rem_adens = np.zeros((5, self.number_of_isotopes))
        dt = h5py.special_dtype(vlen=str)
        self.isolib_db = self.f.create_dataset('iso codes', data=self.isolib,
                                               dtype=dt)

        self.driver_adens_0[0, :] = self.dict_to_array(self.bumat_dict[self.driver_mat_name])
        self.driver_adens_1[0, :] = self.dict_to_array(self.bumat_dict[self.driver_mat_name])
        self.blanket_adens_0[0, :] = self.dict_to_array(self.bumat_dict[self.blanket_mat_name])
        self.blanket_adens_1[0, :] = self.dict_to_array(self.bumat_dict[self.blanket_mat_name])
        self.init_u238 = self.driver_adens[0, self.find_iso_indx('U238')]


    def dict_to_array(self, bumat_dict):
        """ Converts an OrderedDict to an array of its values
        
        Parameters:
        -----------
        bumat_dict: OrderedDict
            key: isotope name
            value: adensity

        Returns:
        --------
        array of bumat_dict values
        """
        array = np.array([])
        for key, value in bumat_dict.items():
            array = np.append(array, value)
        return array


    def reopen_db(self, restart):
        """ Reopens the previously exisiting database

        Parameters:
        -----------
        restart: bool
            if True, modified current_step and datasets
            if False, simply load the datasets
        """   
        self.f = h5py.File(self.db_file, 'r+')
        self.keff_db = self.f['keff_EOC']
        self.keff_db_0 = self.f['keff_BOC']
        self.driver_adens_0 = self.f['driver adensity before reproc']
        self.driver_adens_1 = self.f['driver adensity after reproc']
        self.blanket_adens_0 = self.f['blanket adensity before reproc']
        self.blanket_adens_1 = self.f['blanket adensity after reproc']
        self.tank_adens_db = self.f['tank adensity']
        self.refill_tank_db = self.f['refill tank adensity']
        self.isolib_db = self.f['iso codes']
        self.number_of_isotopes = len(self.isolib_db)
        self.keff = self.keff_db[0, :]

        if restart:
            # set past time
            # !! this time thing should be made certain
            self.current_step = np.amax(np.nonzero(self.keff)) + 1

            # resize datasets
            self.keff_db.resize((2, self.steps + self.current_step))
            self.keff_db_0.resize((2, self.steps + self.current_step))
            shape = (self.steps + self.current_step +
                     1, self.number_of_isotopes)
            self.driver_adens_0.resize(shape)
            self.driver_adens_1.resize(shape)
            self.blanket_adens_0.resize(shape)
            self.blanket_adens_1.resize(shape)
            self.tank_adens_db.resize(shape)
            self.refill_tank_db.resize(shape)
            self.rem_adens = np.zeros((5, self.number_of_isotopes))
            self.th232_adens_0 = self.bu_adens_db_0[0, self.th232_id]

    def read_res(self, moment):
        """ Reads using PyNE the SERPENT output .res file   

        Parameters:
        -----------
        moment: int
            moment of depletion step (0 for BOC and 1 for EOC)

        Returns:
        --------
        [mean_keff, uncertainty_keff]
        """
        res_filename = os.path.join(self.input_file + "_res.m")
        res = serpent.parse_res(res_filename)
        keff_analytical = res['IMP_KEFF']
        return keff_analytical[moment]


    def read_bumat(self, moment):
        """ Reads the SERPENT .bumat file

        Parameters:
        -----------
        moment: int
            moment of depletion step (0 for BOC and 1 for EOC)
        mat_name: string
            name of material to return the composition of

        Returns:
        --------
        bumat_dict: dictionary
            key: material name
            value: dictionary
                key: isotope
                value: adens
        mat_def_dict: dictionary
            key: material name
            value: material definition in SERPENT with volume and density
        """
        bumat_filename = os.path.join('%s.bumat%i' % (self.input_file, moment))
        bumat_dict = OrderedDict({})
        matdef_dict = OrderedDict({})
        # save isonames for mat file generation
        self.isoname = []

        with open(bumat_filename, 'r') as data:
            lines = data.readlines()
            bumat_dict = {}
            gather = False
            for line in lines:
                if 'mat' in line:
                    key = line.split()[1]
                    matdef_dict[key] = line.strip()
                    gather = True
                elif gather:
                    self.isoname.append(line.split()[0])
                    iso = self.isotope_naming(line.split()[0])
                    bumat_dict[key][iso] = float(line.split()[1])
            self.isoname = set(self.isoname)
            self.isolib_db = bumat_dict[key].keys()

        # selectively return the material composition
        # and definition
        return bumat_dict, matdef_dict

    def isotope_naming(self, iso):
        """ This function figures out the isotope naming problem
            by taking into account different anomalies.

        Parameters:
        -----------
        iso: string
            isotope to be converted into name

        Returns:
        --------
        isotope with format [chemical symbol][atmoic weight]
        (e.g. 'Th232', 'U235', 'Cs137')
        """
        if '.' in iso:
            output = iso.split('.')[0] + '0'
            output = nucname.name(output)
        else:
            output = nucname.name()

        # check metastable states
        if output[-1] == 'M':
            metastable_state = iso[-1]
            output = iso + '-' + str(metastable_state)

        return output

    def write_mat_file(self):
        """ Writes the input fuel composition input file block

        Parameters:
        -----------

        Returns:
        --------
        null. creates SEPRENT input mat block text file
        """
        ana_keff_boc = self.read_res(0)
        ana_keff_eoc = self.read_res(1)
        matf = open(self.mat_file, 'w')
        matf.write('%% Step number # %i %f +- %f;%f +- %f \n' %
                   (self.current_step, ana_keff_boc[0], ana_keff_boc[1],
                    ana_keff_eoc[0], ana_keff_eoc[1]))
        for key, val in self.core.items():
            matf.write(self.matdef_dict[key] + ' burn 1 rgb 253 231 37\n')
            for iso in range(self.number_of_isotopes):
                matf.write('%s\t\t%s\n' %(str(self.isoname[iso]), str(val[iso])))
        matf.close()

    def process_fuel(self):
        """ processes the fuel from the output of the previous SERPENT run
            by removing isotopes and refilling with fresh fuel
        """

        # read bumat1 (output composition)
        self.core, self.matdef_dict = self.read_bumat(1)

        # convert core from dict to array
        for key, val in self.core.items():
            self.core[key] = self.dict_to_array(self.core[key])
        
        # record core composition before reprocessing to db_0
        self.driver_adens_0[self.current_step, :] = self.core[self.driver_mat_name]
        self.blanket_adens_0[self.current_step, :] = self.core[self.blanket_mat_name]

        # start reprocessing and refilling
        # reprocess out pa233
        # every 1 step = 3days
        u238_id = self.find_iso_indx('U238')
        u235_id = self.find_iso_indx('U235')

        #### REPROCESSING FROM BLANKET ###########
        # separate pu from blanket and put into driver
        pu = self.find_iso_indx(['Pu'])
        pu_from_blanket = self.remove_iso(pu, 1, self.blanket_mat_name)
        self.core[self.driver_mat_name] += pu_from_blanket

        #### REPROCESSING FROM DRIVER ############
        # remove volatile gases
        # every 1 step = 3 days (30secs)
        volatile_gases = self.find_iso_indx(['Kr', 'Xe', 'Ar', 'Ne', 'H', 'N', 'O', 'Rn'])
        self.rem_adens[0, ] = self.remove_iso(volatile_gases, 1, self.driver_mat_name)

        # remove noble metals
        noble_metals = self.find_iso_indx(['Se', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd',
                                           'Ag', 'Sb', 'Te', 'Zr', 'Cd', 'In', 'Sn'])
        self.rem_adens[1, ] = self.remove_iso(noble_metals, 1, self.driver_mat_name)

        # remove rare earths
        rare_earths = self.find_iso_indx(['Y', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm',
                                          'Gd', 'Eu', 'Dy', 'Ho', 'Er', 'Tb', 'Ga',
                                          'Ge', 'As', 'Zn'])
        self.rem_adens[2, ] = self.remove_iso(rare_earths, 1, self.driver_mat_name)

        # remove every 10 years
        if self.current_step % 1216 == 0:
            discard = self.find_iso_indx(['Cs', 'Ba', 'Rb', 'Sr', 'Li', 'Be',
                                             'Cl', 'Na' 'Th'])
            self.rem_adens[3, ] = self.remove_iso(discard_id, 1, self.driver_mat_name)


        #### REFILLING BLANKET ################
        # fill it back with depleted uranium (0.3 % U235)
        pu_removed = sum(pu_from_blanket)
        tails_enrich = 0.003
        u238_fill = pu_removed * (1 - tails_enrich)
        u235_fill = pu_removed * (tails_enrich)
        self.refill(u238_id, u238_fill, self.blanket_mat_name)
        self.refill(u235_id, u235_fill, self.blanket_mat_name)
        # values are negative to be consistent with previous saltproc
        self.refill_tank_db[self.current_step, u238_id] = -1.0 * u238_fill
        self.refill_tank_db[self.current_step, u235_id] = -1.0 * u235_fill

        #### REFILLING DRIVER ################
        adens_reprocessed_out = sum(self.rem_adens.sum(axis=0))
        u238_fill = adens_reprocessed_out * (1 - tails_enrich)
        u235_fill = adens_reprocessed_out * (tails_enrich)
        self.refill(u238_id, u238_fill, self.driver_mat_name)
        self.refill(u235_id, u235_fill, self.driver_mat_name)
        # note the addition
        self.refill_tank_db[self.current_step, u238_id] += -1.0 * u238_fill
        self.refill_tank_db[self.current_step, u235_id] += -1.0 * u235_fill

        # write the processed material to mat file for next run
        self.write_mat_file()


    def record_db(self):
        """ Records the processed fuel composition, Keff values,
            waste tank composition to database
        """
        self.keff_db[:, self.current_step - 1] = self.read_res(1)
        self.keff_db_0[:, self.current_step - 1] = self.read_res(0)

        self.driver_adens_1[self.current_step, :] = self.core[self.driver_mat_name]
        self.blanket_adens_1[self.current_step, :] = self.core[self.blanket_mat_name]

        self.tank_adens_db[self.current_step, :] = (self.tank_adnes_db[self.current_step - 1, :]
                                                    + self.rem_adens.sum(axis=0))        
        self.f.close()

    def run_serpent(self):
        """ Runs SERPENT with subprocess with the given parameters"""
        # !why a string not a boolean
        if self.bw:
            args = ('aprun', '-n', str(self.nodes), '-d', str(32),
                    self.exec_path,
                    '-omp', str(32), self.input_file)
        else:
            args = (self.exec_path,
                    '-omp', str(self.cores), self.input_file)
        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        print(popen.stdout.read())

    def remove_iso(self, target_iso, removal_eff, region):
        """ Removes isotopes with given removal efficiency

        Parameters:
        -----------
        target_iso: array
            array  of indices for isotopes to remove from core
        removal_eff: float
            removal efficiency (max 1)
        region: string
            region to perform action on

        Returns:
        --------
        tank_stream: array
            array of adens of removed material
        """
        tank_stream = np.zeros(self.number_of_isotopes)
        for iso in target_iso:
            tank_stream[iso] = self.core[reigon][iso] * removal_eff
            # remaining
            self.core[region][iso] = (1 - removal_eff) * self.core[iso]
        return tank_stream

    def refill(self, refill_iso, delta_adens, region):
        """ Refills isotope with target rate of refuel

        Parameters:
        -----------
        refill_iso: array
            array of indices for isotopes to be refilled
        delta_adens: float
            adens to be refilled
        region: string
            region to perform action on


        Returns:
        --------
        null.
        """
        for iso in refill_iso:
            self.core[region][iso] = self.core[region][iso] + delta_adens

    def maintain_const(self, target_isotope, target_adens, region):
        """ Maintains the constant amount of a target isotope

        Parameters:
        -----------
        target_isotope: array
            array of indices for isotopes to be refilled
        target_adens: float
            adens to be satisfied
        region: string
            region to perform action on

        Returns:
        --------
        null.
        """
        tank_stream = np.zeros(self.number_of_isotopes)
        for iso in target_isotope:
            tank_stream[iso] = self.core[region][iso] - target_adens
            self.core[region][iso] = target_adens
        return tank_stream

    def main(self):
        """ Core of saltproc, moves forward in timesteps,
            run serpent, process fuel, record to db, and repeats
        """
        if self.restart and os.path.isfile(self.mat_file):
            try:
                self.f = h5py.File(self.db_file, 'r+')
            except:
                raise ValueErorr('HDF5 file does not exist. You might want to check the '
                                 'restart parameter.') 
            self.reopen_db(True)
            self.steps += self.current_step
            # sets the current step so the db isn't initialized again
        else:
            shutil.copy(self.mat_file, 'init_mat_file')

        while self.current_step < self.steps:
            print('Cycle number of %i of %i steps' %
                  (self.current_step + 1, self.steps))
            self.run_serpent()
            if self.current_step == 0:
                # intializing db to get all arrays for calculation
                self.init_db()
            else:
                self.reopen_db(False)
            self.current_step += 1
            self.process_fuel()
            self.record_db()

        print('End of Saltproc.')
