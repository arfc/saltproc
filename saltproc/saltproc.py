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


class saltproc:
    """ Class saltproc runs SERPENT and manipulates its input and output files
        to reprocess its material, while storing the SERPENT run results in a
        HDF5 database.
    """

    def __init__(self, steps, cores, nodes, bw, restart=False,
                 input_file='core', db_file='db_saltproc.hdf5',
                 mat_file='fuel_comp'):
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
        restart: bool
            if true, starts from an existing database
        input_file: string
            name of input file
        db_file: string
            name of output hdf5 file
        mat_file: string
            name of material file connected to input file
        """
        # initialize all object attributes
        self.steps = steps
        self.cores = cores
        self.nodes = nodes
        self.bw = bw
        self.restart = restart
        self.input_file = input_file
        self.db_file = db_file
        self.mat_file = mat_file
        self.current_step = 0
        self.init_indices()

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

    def init_indices(self):

        self.pa233_id = find_iso_indx('Pa233')
        self.th232_id = find_iso_indx('Th232')
        self.u233_id = find_iso_indx('U233')

        self.kr_id = find_iso_indx('Kr')
        self.xe_id = find_iso_indx('Xe')
        
        self.noble_id = find_iso_indx(['Se', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag',
                                       'Sb', 'Te'])

        self.se_noble_id = find_iso_indx(['Zr', 'Cd', 'In', 'Sn'])

        self.vol_fluorides = find_iso_indx(['Br', 'I'])

        self.rees_id = find_iso_indx(['Y', 'Gd', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm'])

        self.eu_id = find_iso_indx('Eu')

        self.discard_id = find_iso_indx(['Rb', 'Sr', 'Cs', 'Ba'])
        # Higher nuclides (Np-237 and Pu-242), interval 16 years (5840 days)
        self.higher_nuc = find_iso_indx(['Pu237', 'Pu242'])

    def init_db(self):
        """ Initializes the database from the output of the first
            SEPRENT run """

        self.f = h5py.File(self.db_file, 'w')
        # put in values from initial condition
        self.bumat_dict, mat_def = self.read_bumat(self.input_file, 0)

        # initialize isotope library and number of isotpes
        self.isolib = []
        for key in bumat_dict.keys():
            # needs to incode to put string in h5py
            self.isolib.append(key.encode('utf8'))

        self.number_of_isotopes = len(isolib)

        shape = (2, self.steps)
        maxshape = (2, None)
        self.keff_db = self.f.create_dataset('keff_EOC', shape,
                                             maxshape=maxshape, chunks=True)
        self.keff_db_0 = self.f.create_dataset('keff_BOC', shape,
                                               maxshape=maxshape, chunks=True)

        shape = (self.steps + 1, self.number_of_isotopes)
        maxshape = (None, self.number_of_isotopes)
        self.bu_adens_db_0 = self.f.create_dataset('core adensity before reproc',
                                                   shape, maxshape=maxshape,
                                                   chunks=True)
        self.bu_adens_db_1 = self.f.create_dataset('core adensity after reproc',
                                                   shape, maxshape=maxshape,
                                                   chunks=True)
        self.tank_adens_db = self.f.create_dataset('tank adensity',
                                                   shape, maxshape=maxshape,
                                                   chunks=True)
        self.noble_adens_db = self.f.create_dataset('noble adensity',
                                                    shape, maxshape=maxshape,
                                                    chunks=True)
        self.th_adens_db = self.f.create_dataset('Th tank adensity',
                                                 shape, maxshape=maxshape,
                                                 chunks=True)
        # !! raffinate stream consider splitting by what element
        self.rem_adens = np.zeros((5, self.number_of_isotopes))
        dt = h5py.special_dtype(vlen=str)
        self.isolib_db = self.f.create_dataset('iso codes', data=self.isolib,
                                               dtype=dt)

        self.bu_adens_db_0[0, :] = self.dict_to_array(bumat_dict)
        # !! shouldn't this be eoc_adens???
        # !! old code = isolib, bu_adens_db_1[0, :], mat_def = read_bumat(
        # !!          sss_input_file, 0)
        self.bu_adens_db_1[0, :] = self.dict_to_array(bumat_dict)
        # not sure if this will work
        self.th232_adens_0 = bumat_dict['Th232']

    def dict_to_array(self, bumat_dict):
        """ Converts an OrderedDict to an array
        
        Parameters:
        -----------
        bumat_dict: OrderedDict
            key: isotope name
            value: adensity
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
        self.keff_db = self.f['keff_BOC']
        self.keff_db_0 = self.f['keff_BOC']
        self.bu_adens_db_0 = self.f['core adensity before reproc']
        self.bu_adens_db_1 = self.f['core adensity after reproc']
        self.tank_adens_db = self.f['tank adensity']
        self.noble_adens_db = self.f['noble adensity']
        self.th_adens_db = self.f['Th tank adensity']
        isolib_db = self.f['iso codes']
        self.number_of_isotopes = len(isolib_db)
        self.keff = self.keff_db[0, :]

        self.isolib = isolib_db
        if restart:
            # set past time
            # !! this time thing should be made certain
            self.current_step = np.amax(np.nonzero(self.keff)) + 1

            # resize datasets
            self.keff_db.resize((2, self.steps + self.current_step))
            self.keff_db_0.resize((2, self.steps + self.current_step))
            shape = (self.steps + self.current_step +
                     1, self.number_of_isotopes)
            self.bu_adens_db_0.resize(shape)
            self.bu_adens_db_1.resize(shape)
            self.tank_adens_db.resize(shape)
            self.noble_adens_db.resize(shape)
            self.th_adens_db.resize(shape)
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

    def read_bumat(self, file_name, moment):
        """ Reads the SERPENT .bumat file

        Parameters:
        -----------
        moment: int
            moment of depletion step (0 for BOC and 1 for EOC)

        Returns:
        --------
        bumat_dict: dictionary
            key: isotope name
            value: adens
        mat_def: str
            material definition in SERPENT with volume and density
        """
        bumat_filename = os.path.join('%s.bumat%i' % (self.input_file, moment))
        bumat_dict = OrderedDict({})
        with open(bumat_filename, 'r') as data:
            # this should be changed for two region flows
            for line in itertools.islice(
                    data, 5, 6):    # Read material description in variable
                mat_def = line.strip()
            for line in itertools.islice(
                    data, 0, None):  # Skip file header start=6, stop=None
                iso = nucname.name(p[0].split('.')[0])
                bumat_dict[iso] = float(p[1])
        return bumat_dict, mat_def

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
        matf.write(self.mat_def + ' burn 1 rgb 253 231 37\n')
        for iso in range(self.number_of_isotopes):
            matf.write('%s\t\t%s\n' %
                       (str(self.isolib[iso]), str(self.core[iso])))
        matf.close()

    def process_fuel(self):
        """ processes the fuel from the output of the previous SERPENT run
            by removing isotopes and refilling with fresh fuel
        """

        # read bumat1 (output composition)
        isolib, self.core, self.mat_def = self.read_bumat(self.input_file, 1)

        # record core composition before reprocessing to db_0
        self.bu_adens_db_0[self.current_step, :] = self.core

        # start reprocessing and refilling
        # reprocess out pa233
        # every 1 step = 3days
        self.tank_adens_db[self.current_step,
                           ] = self.remove_iso(self.pa_id, 1)
        # add back u233 to core
        # !! where is this refill coming from?
        u233_to_add = self.tank_adens_db[self.current_step, self.pa233_id]
        self.refill(self.u233_id, u233_to_add)

        # remove volatile gases
        # every 1 step = 3 days
        volatile_gases = np.hstack((self.kr_id, self.xe_id, self.noble_id))
        self.rem_adens[0, ] = self.remove_iso(volatile_gases, 1)

        # !! this rem_adens indexing looks wrong
        # remove seminoble metals
        # every 67 steps = 201 days
        if self.current_step % 67 == 0:
            self.rem_adens[1, ] = self.remove_iso(
                np.hstack((self.se_noble_id)), 1)

        # remove volatile fluorides
        # every 20 steps = 60 days
        if self.current_step % 20 == 0:
            self.rem_adens[2, ] = self.remove_iso(
                np.hstack((self.vol_fluorides)), 1)

        # remove REEs
        # evrey 17 steps = 50 days
        if self.current_step % 17 == 0:
            self.rem_adens[3, ] = self.remove_iso(np.hstack((self.rees_id)), 1)

        # remove Eu
        # evrey 167 steps = 500 days
        if self.current_step % 167 == 0:
            self.rem_adens[4, ] = self.remove_iso(
                np.hstack((self.eu_id)), 1)

        # remove Rb, Sr, Cs, Ba
        # every 1145 steps = 3435 days
        if self.current_step % 1145 == 0:
            self.rem_adens[4, ] = self.remove_iso(
                np.hstack((self.discard_id)), 1)

        # remove np-237, pu-242
        # every 1946 steps = 16 years
        if self.current_step % 1946 == 0:
            self.rem_adens[4, ] = self.remove_iso(
                np.hstack((self.higher_nuc)), 1)

        # refill th232 to keep adens constant
        # do it every time
        # if want to do it less often do:
        # if current_step % time == 0:
        self.th_adens_db[self.current_step, ] = self.maintain_const(self.th232_id,
                                                                    self.th232_adens_0)

        # write the processed material to mat file for next run
        self.write_mat_file()

    def record_db(self):
        """ Records the processed fuel composition, Keff values,
            waste tank composition to database
        """
        self.keff_db[:, self.current_step - 1] = self.read_res(1)
        self.keff_db_0[:, self.current_step - 1] = self.read_res(0)
        self.bu_adens_db_1[self.current_step, :] = self.core
        self.tank_adens_db[self.current_step, :] = (self.tank_adens_db[self.current_step - 1, :]
                                                    + self.rem_adens.sum(axis=0))
        # store amount of Th tank
        prev_th = self.th_adens_db[self.current_step - 1, self.th232_id]
        orig_th = self.bu_adens_db_0[0, self.th232_id]
        step_th = self.bu_adens_db_0[self.current_step, self.th232_id]
        self.th_adens_db[self.current_step,
                         self.th232_id] = prev_th - orig_th - step_th
        self.f.close()

    def run_serpent(self):
        """ Runs SERPENT with subprocess with the given parameters"""
        # !why a string not a boolean
        if self.bw:
            args = ('aprun', '-n', str(self.nodes), '-d', str(32),
                    '/projects/sciteam/bahg/serpent30/src/sss2',
                    '-omp', str(32), self.input_file)
        else:
            args = ('/home/andrei2/serpent/serpetn2/src_test/sss2',
                    '-omp', str(self.cores), self.input_file)
        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        print(popen.stdout.read())

    def remove_iso(self, target_iso, removal_eff):
        """ Removes isotopes with given removal efficiency

        Parameters:
        -----------
        target_iso: array
            array  of indices for isotopes to remove from core
        removal_eff: float
            removal efficiency (max 1)

        Returns:
        --------
        tank_stream: array
            array of adens of removed material
        """
        tank_stream = np.zeros(self.number_of_isotopes)
        for iso in target_iso:
            tank_stream[iso] = self.core[iso] * removal_eff
            self.core[iso] = (1 - removal_eff) * self.core[iso]
        return tank_stream

    def refill(self, refill_iso, delta_adens):
        """ Refills isotope with target rate of refuel

        Parameters:
        -----------
        refill_iso: array
            array of indices for isotopes to be refilled
        delta_adens: float
            adens to be refilled

        Returns:
        --------
        null.
        """

        for iso in refill_iso:
            self.core[iso] = self.core[iso] + delta_adens

    def maintain_const(self, target_isotope, target_adens):
        """ Maintains the constant amount of a target isotope

        Parameters:
        -----------
        target_isotope: array
            array of indices for isotopes to be refilled
        target_adens: float
            adens to be satisfied

        Returns:
        --------
        null.
        """
        # !this is funky
        tank_stream = np.zeros(self.number_of_isotopes)
        for iso in target_isotope:
            tank_stream[iso] = self.core[iso] - target_adens
            self.core[iso] = target_adens
        return tank_stream

    def main(self):
        """ Core of saltproc, moves forward in timesteps,
            run serpent, process fuel, record to db, and repeats
        """
        # !!why not boolean (you can do 0 and 1)
        if self.restart and os.path.isfile(self.mat_file):
            self.f = h5py.File(self.db_file, 'r+')
            self.reopen_db(True)
            self.steps += self.current_step
            # sets the current step so the db isn't initialized again
        else:
            # !!this shouldn't be hardcoded
            shutil.copy('fuel_comp_with_fix', self.mat_file)

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
