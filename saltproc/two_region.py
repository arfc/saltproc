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

        self.fissile_add_back_frac = 0.5

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

        self.get_isos()
        self.get_mat_def()
        self.dep_dict = self.read_dep()

        self.number_of_isotopes = len(self.isoname)
        shape = (2, self.steps)
        maxshape = (2, None)
        self.keff_eoc_db = self.f.create_dataset('keff_EOC', shape,
                                             maxshape=maxshape, chunks=True)
        self.keff_boc_db = self.f.create_dataset('keff_BOC', shape,
                                               maxshape=maxshape, chunks=True)

        shape = (self.steps + 1, self.number_of_isotopes)
        maxshape = (None, self.number_of_isotopes)
        print('INIT DB ')
        print('NUMBER OF ISOTOPES: %i' %self.number_of_isotopes)
        print(shape)
        self.driver_before_db = self.f.create_dataset('driver composition before reproc',
                                                   shape, maxshape=maxshape,
                                                   chunks=True)
        print(len(self.driver_before_db[0, :]))
        self.driver_after_db = self.f.create_dataset('driver composition after reproc',
                                                   shape, maxshape=maxshape,
                                                   chunks=True)
        self.blanket_before_db = self.f.create_dataset('blanket composition before reproc',
                                                     shape, maxshape=maxshape,
                                                     chunks=True)
        self.blanket_after_db = self.f.create_dataset('blanket composition after reproc',
                                                     shape, maxshape=maxshape,
                                                     chunks=True)
        self.fissile_tank_db = self.f.create_dataset('fissile tank composition', shape, maxshape=maxshape,
                                             chunks=True)
        self.waste_tank_db = self.f.create_dataset('waste tank composition',
                                                   shape, maxshape=maxshape,
                                                   chunks=True)
        self.driver_refill_tank_db = self.f.create_dataset('driver refill tank composition',
                                                          shape, maxshape=maxshape,
                                                          chunks=True)
        self.blanket_refill_tank_db = self.f.create_dataset('blanket refill tank composition',
                                                            shape, maxshape=maxshape,
                                                            chunks=True)
        dt = h5py.special_dtype(vlen=str)
        # have to encode to utf8 for hdf5 string
        self.isolib_db = self.f.create_dataset('iso names',
                                               data=[x.encode('utf8') for x in self.isoname],
                                               dtype=dt)
        # the first depleted, non-reprocessed fuel is stored in timestep 1
        self.driver_before_db[0, :] = self.dep_dict[self.driver_mat_name]
        self.driver_after_db[0, :] = self.dep_dict[self.driver_mat_name]
        self.blanket_before_db[0, :] = self.dep_dict[self.blanket_mat_name]
        self.blanket_after_db[0, :] = self.dep_dict[self.blanket_mat_name]


    def reopen_db(self, restart):
        """ Reopens the previously exisiting database

        Parameters:
        -----------
        restart: bool
            if True, modified current_step and datasets
            if False, simply load the datasets
        """   
        self.f = h5py.File(self.db_file, 'r+')
        self.keff_eoc_db = self.f['keff_EOC']
        self.keff_boc_db = self.f['keff_BOC']
        self.driver_before_db = self.f['driver composition before reproc']
        print(len(self.driver_before_db[0, :]))

        self.driver_after_db = self.f['driver composition after reproc']
        self.blanket_before_db = self.f['blanket composition before reproc']
        self.blanket_after_db = self.f['blanket composition after reproc']
        self.waste_tank_db = self.f['waste tank composition']
        self.driver_refill_tank_db = self.f['driver refill tank composition']
        self.blanket_refill_tank_db = self.f['blanket refill tank composition']
        self.isolib_db = self.f['iso names']
        self.fissile_tank_db = self.f['fissile tank composition']


        if restart:

            self.get_isos()
            self.get_mat_def()
            self.number_of_isotopes = len(self.isoname)
            self.keff = self.keff_eoc_db[0, :]
            # set past time
            # !! this time thing should be made certain
            self.current_step = np.amax(np.nonzero(self.keff)) + 1

            # resize datasets
            self.keff_eoc_db.resize((2, self.steps + self.current_step))
            self.keff_boc_db.resize((2, self.steps + self.current_step))
            shape = (self.steps + self.current_step +
                     1, self.number_of_isotopes)
            self.driver_before_db.resize(shape)
            self.driver_after_db.resize(shape)
            self.blanket_before_db.resize(shape)
            self.blanket_after_db.resize(shape)
            self.waste_tank_db.resize(shape)
            self.driver_refill_tank_db.resize(shape)
            self.blanket_refill_tank_db.resize(shape)
            self.fissile_tank_db.resize(shape)

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
        dep_dict: dictionary
            key: material name
            value: dictionary
                key: isotope
                value: adens
        """
        dep_file = os.path.join('%s_dep.m' %self.input_file)
        with open(dep_file, 'r') as f:
            lines = f.readlines()
            self.dep_dict = OrderedDict({})
            read = False
            for line in lines:
                if 'MAT'in line and 'MDENS' in line:
                    key = line.split('_')[1]
                    read = True
                    self.dep_dict[key] = [0] * len(self.isoname)
                elif read and ';' in line:
                    read = False
                elif read:
                    z = line.split(' ')
                    # last burnup stage
                    indx = z.index('%')
                    mdens = z[indx-1]
                    # the isotope name is at the end of the line.
                    name = z[-1].replace('\n', '')
                    # find index so that it doesn't change
                    try:
                        where_in_isoname = self.isoname.index(name)
                        self.dep_dict[key][where_in_isoname] = float(z[indx-1])
                    except ValueError:
                        if name not in ['total', 'data']:
                            print('THIS WAS NOT HERE %s' %name)
        return self.dep_dict


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


    def separate_fuel(self):
        """ separate fissile material from blanket,
            separate waste out of driver
        """
        self.core = self.read_dep()

        # record the depleted composition before reprocessing
        print(len(self.driver_before_db[self.current_step, :]))
        print(len(self.core[self.driver_mat_name]))
        self.driver_before_db[self.current_step, :] = self.core[self.driver_mat_name]
        self.blanket_before_db[self.current_step, :] = self.core[self.blanket_mat_name]

        # waste tank db zero initialization
        self.waste_tank_db[self.current_step, :] = np.zeros(self.number_of_isotopes)

        # reprocess fissile from blanket with removal eff 1
        pu = self.find_iso_indx(['Pu'])
        self.fissile_tank_db[self.current_step, :] = self.remove_iso(pu, 1, self.blanket_mat_name)

        # reprocess waste from driver
        volatile_gases = self.find_iso_indx(['Kr', 'Xe', 'Ar', 'Ne', 'H', 'N', 'O', 'Rn'])
        self.waste_tank_db[self.current_step, :] += self.remove_iso(volatile_gases, 1, self.driver_mat_name)

        # remove noble metals
        noble_metals = self.find_iso_indx(['Se', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd',
                                           'Ag', 'Sb', 'Te', 'Zr', 'Cd', 'In', 'Sn'])
        self.waste_tank_db += self.remove_iso(noble_metals, 1, self.driver_mat_name)

        # remove rare earths
        rare_earths = self.find_iso_indx(['Y', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm',
                                          'Gd', 'Eu', 'Dy', 'Ho', 'Er', 'Tb', 'Ga',
                                          'Ge', 'As', 'Zn'])
        self.waste_tank_db += self.remove_iso(rare_earths, 1, self.driver_mat_name)

        # remove every 10 years
        if self.current_step % 1216 == 0:
            discard = self.find_iso_indx(['Cs', 'Ba', 'Rb', 'Sr', 'Li', 'Be',
                                          'Cl', 'Na' 'Th'])
            self.waste_tank_db += self.remove_iso(discard_id, 1, self.driver_mat_name)
        #### end of separation from driver


    def refuel(self):
        """ After separating out fissile and waste material,
            this function refuels the salt with fissile and fertile
            material
        """
        # refill tank db zero initialization
        self.driver_refill_tank_db[self.current_step, :] = np.zeros(self.number_of_isotopes)
        self.blanket_refill_tank_db[self.current_step, :] = np.zeros(self.number_of_isotopes)

        ########## blanket refilling
        pu_removed = sum(self.fissile_tank_db[self.current_step, :])
        print('\nREMOVED %f GRAMS OF PU FROM BLANKET' %pu_removed)
        # depleted uranium composition
        tails_enrich = 0.003
        # for natural uranium, use below:
        # tails_enrich = 0.007
        u238_fill = pu_removed * (1 - tails_enrich)
        u235_fill = pu_removed * (tails_enrich)

        u238_id = self.find_iso_indx('U238')
        u235_id = self.find_iso_indx('U235')
        self.refill(u238_id, u238_fill, self.blanket_mat_name)
        self.refill(u235_id, u235_fill, self.blanket_mat_name)

        ########## driver refilling
        # refill as much as what's reprocessed for mass balance
        fill_qty = sum(self.waste_tank_db[self.current_step, :])
        print('REMOVED A TOTAL OF %f GRAMS OF WASTE FROM THE DRIVER\n' %fill_qty)

        ### REACTIVITY CONTROL MODULE

        self.reactivity_control()
        pu_to_add = self.fissile_tank_db[self.current_step, :] * self.fissile_add_back_frac
        print('PUTTING IN %f GRAMS OF PU BACK INTO THE DRIVER' %sum(pu_to_add))
        if sum(pu_to_add) >= fill_qty:
            raise ValueError('\n\nThe fissile add back fraction is too high. It causes the driver to increase in mass!!!!\n\n')
        self.fissile_tank_db[self.current_step, :] -= pu_to_add
        self.core[self.driver_mat_name] += pu_to_add

        # fill the rest of the driver with depleted uranium
        fill_qty -= sum(pu_to_add)
        u238_fill = fill_qty * (1 - tails_enrich)
        u235_fill = fill_qty * tails_enrich
        self.refill(u238_id, u238_fill, self.driver_mat_name)
        self.refill(u235_id, u235_fill, self.driver_mat_name)
        print('PUTTING IN %f GRAMS OF DEP U INTO DRIVER\n' %(fill_qty))


    def reactivity_control(self):
        """ Controls fraction of fissile material
            input into core to control keff into
            a range
        """
        # check EOC KEFF for determining fissile_add_back_frac

        self.eoc_keff = self.read_res(1)
        print('EOC KEFF IS %f +- %f' %(eoc_keff[0], eoc_keff[1]))
        ## SOME SMART WAY TO REDUCE OR INCREASE THE AMOUNT OF PU
        ## GOING INSIDE THE CORE DEPENDING ON THE KEFF VALUE
        
       



    def record_db(self):
        """ Records the processed fuel composition, Keff values,
            waste tank composition to database
        """
        self.keff_eoc_db[:, self.current_step - 1] = self.read_res(1)
        self.keff_boc_db[:, self.current_step - 1] = self.read_res(0)

        self.driver_after_db[self.current_step, :] = self.core[self.driver_mat_name]
        self.blanket_after_db[self.current_step, :] = self.core[self.blanket_mat_name]

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
            # print('REMOVING %f GRAMS OF %s FROM %s' %(self.core[region][iso], self.isoname[iso], region))
        return tank_stream

    def refill(self, refill_iso, delta, region):
        """ Refills isotope with target rate of refuel

        Parameters:
        -----------
        refill_iso: array
            array of indices for isotopes to be refilled
        delta: float
            amount to be refilled
        region: string
            region to perform action on


        Returns:
        --------
        null.
        """
        for iso in refill_iso:
            self.core[region][iso] = self.core[region][iso] + delta
            # print('REFILLING %f GRAMS OF %s TO %s' %(delta, self.isoname[iso], region))
            if region == self.driver_mat_name:
                self.driver_refill_tank_db[self.current_step, iso] -= delta
            elif region == self.blanket_mat_name:
                self.blanket_refill_tank_db[self.current_step, iso] -= delta
        
    def maintain_const(self, target_isotope, target_qty, region):
        """ Maintains the constant amount of a target isotope

        Parameters:
        -----------
        target_isotope: array
            array of indices for isotopes to be refilled
        target_qty: float
            quantity to be satisfied
        region: string
            region to perform action on

        Returns:
        --------
        null.
        """
        tank_stream = np.zeros(self.number_of_isotopes)
        for iso in target_isotope:
            tank_stream[iso] = self.core[region][iso] - target_qty
            self.core[region][iso] = tartget_qty
        return tank_stream

    def start_sequence(self):
        """ checks restart and preexisting file
            copies initial mat file to predefined mat file name
        """
        if self.restart and os.path.isfile(self.mat_file):
            try:
                self.f = h5py.File(self.db_file, 'r+')
            except:
                raise ValueError('HDF5 File does not exist.\n'
                                 'Are you sure you want to restart?')
            self.reopen_db(True)
            self.steps += self.current_step

        else:
            if os.path.isfile(self.db_file):
                print('File already exists: the file is moved to old_%s' %self.db_file)
                os.rename(self.db_file, 'old_' + self.db_file)
            print('Copying %s to %s so the initial material file is unchanged..'
                  %(self.init_mat_file, self.mat_file))
            shutil.copy(self.init_mat_file, self.mat_file)

    def main(self):
        """ Core of saltproc: moves forward in timesteps,
            run serpent, process fuel, record to db, and repeats
        """
        self.start_sequence()

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
            self.separate_fuel()
            self.refuel()
            self.write_mat_file()

            ### this is to check if serpent is running
            u235_id = self.find_iso_indx('U235')
            print(self.driver_before_db[self.current_step, u235_id])
            self.record_db()

        print('End of Saltproc.')
