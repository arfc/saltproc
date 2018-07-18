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
import fnmatch


class saltproc_two_region:
    """ Class saltproc runs SERPENT and manipulates its input and output files
        to reprocess its material, while storing the SERPENT run results in a
        HDF5 database. This class is for two region flows, with fertile blanket
        and fissile driver. The fissile material from the blanket is separated
        and put into the driver.
    """

    def __init__(self, steps, cores, nodes, bw, exec_path, restart=False,
                 input_file='core', db_file='db_saltproc.hdf5',
                 mat_file='fuel_comp', init_mat_file='init_mat_file', 
                 driver_mat_name='fuel', blanket_mat_name='blank'):
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
        init_mat_file: string
            name of material file initally definedd by user
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
        self.init_mat_file = init_mat_file
        self.blanket_mat_name = blanket_mat_name
        self.driver_mat_name = driver_mat_name
        self.get_library_isotopes()

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
        indx_list = []
        indx = 0
        if isinstance(keyword, str):
            indx = self.isoname.index(keyword)
            indx_list.append(indx)
        elif isinstance(keyword, list):
            for key in keyword:
                pattern = key + '*'
                matching = fnmatch.filter(self.isoname, pattern)
                for i in matching:
                    indx = self.isoname.index(i)
                    indx_list.append(indx)
        return np.array(indx_list)

    def get_library_isotopes(self):
        """ Returns the isotopes in the cross section library

        Parameters:
        -----------

        Returns:
        --------
        iso_array: array
            array of isotopes in cross section library:
        """
        with open(self.input_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'set acelib' in line:
                    start = line.index('"') + 1
                    end = line[start:].index('"') + start
                    acelib = line[start:end]
        self.lib_isos = []
        with open(acelib, 'r') as f:
            lines = f.readlines()
            for line in lines:
                iso = line.split()[1]
                self.lib_isos.append(iso)

        self.lib_isos = np.array(self.lib_isos)

    def get_mat_def(self):
        """ Get material definition from the initial material definition
            file
        """
        with open(self.init_mat_file, 'r') as f:
            self.mat_def_dict = OrderedDict({})
            lines = f.readlines()
            for line in lines:
                if 'mat' in line:
                    z = line.split()
                    key = z[1]
                    self.mat_def_dict[key] = line

    def get_isos(self):
        """ Reads the isotope zai and name from dep file

        """
        dep_file = os.path.join('%s_dep.m' %self.input_file)
        with open(dep_file, 'r') as f:
            lines = f.readlines()
            read = False
            read_zai = False
            read_name = False
            self.isozai = []
            self.isoname = []
            for line in lines:
                if 'ZAI' in line:
                    read_zai = True
                elif read_zai and ';' in line:
                    read_zai = False
                elif read_zai:
                    self.isozai.append(line.strip())

                if 'NAMES' in line:
                    read_name = True
                elif read_name and ';' in line:
                    read_name = False
                elif read_name:
                    # skip the spaces and first apostrophe
                    self.isoname.append(line.split()[0][1:]) 
                
            self.isozai = self.isozai[:-2]
            self.isoname = self.isoname[:-2]


    def init_db(self):
        """ Initializes the database from the output of the first
            SEPRENT run """

        self.f = h5py.File(self.db_file, 'w')
        # put in values from initial condition
        # only bumat1 will give all isotopes
        self.get_isos()
        self.get_mat_def()
        self.bumat_dict = self.read_dep()

        self.number_of_isotopes = len(self.isoname)
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
        self.blanket_adens_0 = self.f.create_dataset('blanket adensity before reproc',
                                                     shape, maxshape=maxshape,
                                                     chunks=True)
        self.blanket_adens_1 = self.f.create_dataset('blanket adensity after reproc',
                                                     shape, maxshape=maxshape,
                                                     chunks=True)
        self.pu_tank = self.f.create_dataset('pu tank adensity', shape, maxshape=maxshape,
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
        # have to encode to utf8 for hdf5 string
        self.isolib_db = self.f.create_dataset('iso codes',
                                               data=[x.encode('utf8') for x in self.isoname],
                                               dtype=dt)
        self.driver_adens_0[0, :] = self.bumat_dict[self.driver_mat_name]
        self.driver_adens_1[0, :] = self.bumat_dict[self.driver_mat_name]
        self.blanket_adens_0[0, :] = self.bumat_dict[self.blanket_mat_name]
        self.blanket_adens_1[0, :] = self.bumat_dict[self.blanket_mat_name]
        self.init_u238 = self.driver_adens_0[0, self.find_iso_indx('U238')]


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
        self.pu_tank = self.f['pu tank adensity']
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
            self.pu_tank.resize(shape)
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


    def read_dep(self):
        """ Reads the SERPENT _dep.m file

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
        """
        dep_file = os.path.join('%s_dep.m' %self.input_file)
        with open(dep_file, 'r') as f:
            lines = f.readlines()
            self.bumat_dict = OrderedDict({})
            read = False
            for line in lines:
                if 'MAT'in line and 'MDENS' in line:
                    key = line.split('_')[1]
                    read = True
                    self.bumat_dict[key] = [0] * len(self.isoname)
                elif read and ';' in line:
                    read = False
                elif read:
                    z = line.split(' ')
                    # second / last burnup stage
                    indx = z.index('%')
                    mdens = z[indx-1]
                    # find index so that it doesn't change
                    name = z[-1].replace('\n', '')
                    try:
                        where_in_isoname = self.isoname.index(name)
                        self.bumat_dict[key][where_in_isoname] = float(z[indx-1])
                    except ValueError:
                        if name not in ['total', 'data']:
                            print('THIS WAS NOT HERE %s' %name)
        return self.bumat_dict


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
        not_in_lib = open('NOT_IN_LIB', 'w')
        matf = open(self.mat_file, 'w')
        matf.write('%% Step number # %i %f +- %f;%f +- %f \n' %
                   (self.current_step, ana_keff_boc[0], ana_keff_boc[1],
                    ana_keff_eoc[0], ana_keff_eoc[1]))
        for key, val in self.core.items():
            matf.write(self.mat_def_dict[key].replace('\n', '') + ' fix 09c 900\n')
            for indx, isotope in enumerate(self.isozai):
                # filter metastables
                if str(isotope[-1]) != '0':
                    continue
                # change name so it corresponds to temperature
                isotope = str(isotope)[:-1] + '.09c'
                # filter isotopes not in cross section library 
                if isotope not in self.lib_isos:
                    not_in_lib.write('%s\t\t%s\n' %(str(isotope), str(-1.0 * val[indx])))
                    continue
                else:
                    matf.write('%s\t\t%s\n' %(str(isotope), str(-1.0 * val[indx])))
        matf.close()

    def process_fuel(self):
        """ processes the fuel from the output of the previous SERPENT run
            by removing isotopes and refilling with fresh fuel
        """

        # read bumat1 (output composition)
        self.core = self.read_dep()

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
        self.pu_tank[self.current_step, :] = self.remove_iso(pu, 1, self.blanket_mat_name)

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
        pu_removed = sum(self.pu_tank[self.current_step, :])
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
        # fill this amount of plutonium
        # hopefully there's pu leftover
        self.pu_tank[self.current_step, :] -= adens_reprocessed_out * self.find_pu_comp()
        self.core[self.driver_mat_name] += adens_reprocessed_out * self.find_pu_comp()

        #### MAYBE RENORMALIZE BEFORE WRITING MAT FILE?

        # write the processed material to mat file for next run
        self.write_mat_file()

    def find_pu_comp(self):
        """ Finds the separated Pu quality (composition) """
        comp_vec = self.pu_tank[self.current_step, :] / sum(self.pu_tank[self.current_step, :])
        return comp_vec

    def record_db(self):
        """ Records the processed fuel composition, Keff values,
            waste tank composition to database
        """
        self.keff_db[:, self.current_step - 1] = self.read_res(1)
        self.keff_db_0[:, self.current_step - 1] = self.read_res(0)

        self.driver_adens_1[self.current_step, :] = self.core[self.driver_mat_name]
        self.blanket_adens_1[self.current_step, :] = self.core[self.blanket_mat_name]

        self.tank_adens_db[self.current_step, :] = (self.tank_adens_db[self.current_step - 1, :]
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
        print('RUNNNIN')
        output = subprocess.check_output(args)
        print('DONES')
        print(output)

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
            tank_stream[iso] = self.core[region][iso] * removal_eff
            self.core[region][iso] = (1 - removal_eff) * self.core[region][iso]
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
            if os.path.isfile(self.db_file):
                print('FILE ALREADY EXISTS - THE FILE IS MOVED TO old_%s' %self.db_file)
                os.rename(self.db_file, 'old' + self.db_file)
            shutil.copy(self.init_mat_file, self.mat_file)

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
            ### this is to check if serpent is running
            u235_id = self.find_iso_indx('U235')
            print(self.driver_adens_0[self.current_step, u235_id])
            #######
            # self.record_db()

        print('End of Saltproc.')
