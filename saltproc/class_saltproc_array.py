import math
import itertools
import subprocess
import os
import numpy as np
import matplotlib.pyplot
from pyne import serpent
from pyne import nucname
import h5py
import shutil
import argparse


# Parse flags
parser = argparse.ArgumentParser()
parser.add_argument('-r', choices=['True', 'False'])  # Restart flag -r
parser.add_argument(
    '-n',
    nargs=1,
    type=int,
    default=1)         # Number of nodes -n
parser.add_argument(
    '-steps',
    nargs=1,
    type=int,
    default=5)     # Number of steps
parser.add_argument('-bw', choices=['True', 'False'])  # -bw Blue Waters?
args = parser.parse_args()
restart = args.r
nodes = int(args.n[0])
steps = int(args.steps[0])
bw = args.bw


class saltproc:
    def __init__(self, restart=False,
                  input_file='core', db_file='db_saltproc.hdf5',
                  mat_file='fuel_comp', steps, cores):
        self.current_step = 0
        self.init_indices()

        # initial run to get what input / out looks like
        self.run_serpent(self.input_file, self.cores)
        self.init_db()

        while self.current_step < self.steps:
            self.record_db()

    def init_indices(self):
        self.pa_id = np.array([1088])                # ID for Pa-233 (91)
        self.th232_id = np.array([1080])             # IDs for Th-232 (90)
        self.u233_id = np.array([1095])              # ID for U-233 (92)
        self.pa233_id = np.array([1088])             # ID for Pa-233 (91)
        # Volatile gases, interval 20 sec
        self.kr_id = np.arange(217, 240)           # IDs for all isotopes of Kr(36)
        self.xe_id = np.arange(718, 746)           # IDs for all isotopes of Xe(54)
        # Noble metals, interval 20 sec
        self.se_id = np.arange(175, 196)           # IDs for Selenium (34)
        self.nob1_id = np.arange(331, 520)           # All elements from Nb(41) to Ag (47)
        self.nob2_id = np.arange(636, 694)           # All elements from Sb(51) to Te (52)
        self.noble_id = np.hstack((se_id, nob1_id, nob2_id))  # Stack all Noble Metals
        # Seminoble metals, interval 200 days
        self.zr_id = np.arange(312, 331)           # IDs for Zr (40)
        self.semin_id = np.arange(520, 636)           # IDs from Cd(48) to Sn(50)
        self.se_noble_id = np.hstack((zr_id, semin_id))  # Stack all Semi-Noble Metals
        # Volatile fluorides, 60 days
        self.br_id = np.arange(196, 217)           # IDs for Br(35)
        self.i_id = np.arange(694, 718)           # IDs for I(53)
        self.vol_fluorides = np.hstack((br_id, i_id))      # Stack volatile fluorides
        # Rare earth, interval 50 days
        self.y_id = np.arange(283, 312)           # IDs for Y(39)
        self.rees_1_id = np.arange(793, 916)           # IDs for La(57) to Sm(62)
        self.gd_id = np.arange(934, 949)           # IDs for Gd(64)
        # Stack of all Rare earth except Eu
        self.rees_id = np.hstack((y_id, rees_1_id, gd_id))
        # Eu(63)
        self.eu_id = np.arange(916, 934)
        # Discard, 3435 days
        self.rb_sr_id = np.arange(240, 283)        # Rb(37) and Sr(38) vector
        self.cs_ba_id = np.arange(746, 793)        # Cs(55) and Ba(56) vector
        # Stack discard
        self.discard_id = np.hstack((rb_sr_id, cs_ba_id))
        # Higher nuclides (Np-237 and Pu-242), interval 16 years (5840 days)
        self.np_id    = np.array ([1109])         # 237Np93
        self.pu_id    = np.array ([1123])         # 242Pu94
        self.higher_nuc = np.hstack((np_id, pu_id))

    def init_db(self):
        self.f = h5py.File(self.db_file, 'w')
        isolib, adens_array, mat_def = self.read_bumat(self.input_file, 1)
        # initialize keys
        self.number_of_isotopes = len(isolib)

        shape = (2, steps)
        maxshape = (2, None)
        self.keff_db = f.create_dataset('keff_EOC', shape,
                                   maxshape=maxshape, chunks=True)
        self.keff_db_0 = f.create_dataset('keff_BOC', shape,
                                   maxshape=maxshape, chunks=True)

        shape = (self.steps + 1, self.number_of_isotopes)
        maxshape = (None, self.number_of_isotopes)
        self.bu_adens_db_0 = f.create_dataset('core adensity before reproc',
                                               shape, maxshape=maxshape,
                                               chunks=True)
        self.bu_adens_db_1 = f.create_dataset('core adensity after reproc',
                                              shape, maxshape=maxshape,
                                              chunks=True)
        self.tank_adens_db = f.create_dataset('tank adensity',
                                              shape, maxshape=maxshape,
                                              chunks=True)
        self.noble_adens_db = f.create_dataset('noble adensity',
                                               shape, maxshape=maxshape,
                                               chunks=True)
        self.th_adens_db = f.create_dataset('Th tank adensity',
                                             shape, maxshape=maxshape,
                                             chunks=True)
        #! raffinate steram consider splitting by what element
        self.rem_adens = f.create_dataset('Raffinate stream',
                                          (5, self.number_of_isotopes),
                                          chunks=True)
        self.isolib_db = f.create_dataset('iso codes', data=self.isolib_array,
                                          dtype=dt)

        # put in values from initial condition
        isolib, boc_adens, mat_def = self.read_bumat(self.input_file, 0)
        bu_adens_db_0[0, :] = boc_adens
        #! shouldn't this be eoc_adens???
        #! old code = isolib, bu_adens_db_1[0, :], mat_def = read_bumat(
        #!          sss_input_file, 0)
        bu_adens_db_1[0, :] = boc_adens
        th232_adens_0 = boc_adens[self.th232_id]



    def read_res(self, moment):
        """ Reads the .res file generated from serpent using PyNE

        Parameters:
        -----------
        moment: int
            moment of depletion step (0 for BOC and 1 for EOC)

        Returns:
        --------
        [mean_keff, uncertainty_keff]
        """
        res_filename = os.path.join(self.inp_filename + "_res.m")
        res = serpent.parse_res(res_filename)
        keff_analytical = res['IMP_KEFF']
        return keff_analytical[moment]


    def read_bumat(self, file_name, moment):
        """ Reads the .bumat file generated from serpent

        Parameters:
        -----------
        moment: int
            moment of depletion step (0 for BOC and 1 for EOC)

        Returns:
        --------
        isolib_array: np array
            array of isotopes
        bu_adens: list
            list of isotopes adens
        mat_def: str
            material definition in SERPENT with volume and density
        """
        bumat_filename = os.path.join('%s.bumat%i' %(self.file_name, moment))
        with open(bumat_filename, 'r') as data:
            isolib = []
            bu_adens = []
            for line in itertools.islice(
                    data, 5, 6):    # Read material description in variable
                mat_def = line.strip()
            for line in itertools.islice(
                    data, 0, None):  # Skip file header start=6, stop=None
                p = line.split()
                isolib.append(str(p[0]))
                bu_adens.append(float(p[1]))
        isolib_array = np.asarray(isolib)
        return isolib_array, bu_adens, mat_def

    def write_mat_file(self):
        """ Writes the input fuel composition input file block

        Parameters:
        -----------
        file_name: str
            name of output file
        dep_dict: dictionary
            key: isotope name
            val: adens
        fuel_intro: str
            fuel definition line defining fuel properties
        current_step: int
            step number

        Returns:
        --------
        null. outputs SEPRENT input mat block
        """
        ana_keff_boc = read_res(sss_input_file, 0)
        ana_keff_eoc = read_res(sss_input_file, 1)
        matf = open(file_name, 'w')
        matf.write('% Step number # %i %f %f \n' %(current_step, ana_keff_boc, ana_keff_eoc))
        matf.write(fuel_intro + ' burn 1 rgb 253 231 37\n')
        for iso, adens in dep_dict.items():
            matf.write('%s\t %f\n' %(iso, adens))
        matf.close()

    def record_db(self):
        # read bumat1
        isolib, buadens, mat_def = self.read_bumat(self.input_file, 1)
        self.core = buadens
        self.bu_adens_db_0[self.current_step, :] = self.core

        # start reprocessing and refilling
        # reprocess out pa233
        # every 1 step = 3days
        self.tank_adens_db[self.current_step, ] = self.reprocess_iso(self.pa_id, 1, 1)
        # add back u233 to core
        #! where is this refill coming from?
        u233_to_add = self.tank_adens_db[self.current_step, self.pa233_id]
        self.refill(self.u233_id, u233_to_add)

        # remove volatile gases
        # every 1 step = 3 days
        volatile_gases = np.hstack(self.kr_id, self.xe_id, self.noble_id)
        self.rem_adens[0, ] = self.reprocess_iso(volatile_gases, 1, 1)

        # remove seminoble metals
        # every 67 steps = 201 days
        self.rem_adens[1, ] = self.reprocess_iso(np.hstack((self.se_noble_id)), 1, 67)

        # remove volatile fluorides
        # every 20 steps = 60 days
        self.rem_adens[2, ] = self.reprocess_iso(np.hstack(self.vol_fluorides), 1, 20)

        # remove REEs
        # evrey 17 steps = 50 days
        self.rem_adens[3, ] = self.reprocess_iso(np.hstack(self.rees_id), 1, 17)

        # remove Eu
        # evrey 167 steps = 500 days
        self.rem_adens[4, ] = self.reprocess_iso(np.hstack(self.eu_id), 1, 167)

        # remove Rb, Sr, Cs, Ba
        # every 1145 steps = 3435 days
        self.rem_adens[4, ] = self.reprocess_iso(np.hstack(self.discard_id), 1, 1145)

        # remove np-237, pu-242
        # every 1946 steps = 16 years
        self.rem_adens[4, ] = self.reprocess_iso(np.hstack(self.higher_nuc), 1, 1946)

        # refill th232 to keep adens constant
        
        


    def reprocess_iso(self, target_iso, removal_eff, removal_interval):
        tank_stream = np.zeros(self.number_of_isotopes)
        if self.current_step % removal_interval == 0:
            for iso in target_isotope:
                tank_stream[iso] = self.core[iso] * removal_eff
                self.core[iso] = (1 - removal_eff) * self.core[iso]
        return tank_stream

    def refill(self, refill_iso, delta_adens):
        for iso in refill_iso:
            self.core[iso] = self.core[iso] + delta_adens

