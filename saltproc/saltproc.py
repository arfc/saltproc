# Import modules
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


restart = 'False'                      # Restart option off by default
# Serpent 2 file without fuel description and geometry
sss_input_file = 'core'
db_file = 'db_saltproc.hdf5'           # output HDF5 database name
# dep_file       =   'core_dep.m'              # Path and name depletion output from Serpent
# bumat_file     = 'core.bumat1'               # Path and name depletion
# output from Serpent
# Path and name of file with materials data (input for Serpent)
mat_file = 'fuel_comp'
cores = 4                         # Number of OMP cores to use on Workstation
nodes = 1                          # Number of nodes by defaule
bw = 'False'                       # Not cluster by default
steps = 5                          # 5 fuel cycle steps by default
# Isotopes description
# ID of isotope for which we want to keep constant adens (Pa-233, 232,234,235)
pa_id = np.array([1088])                # ID for Pa-233 (91)
th232_id = np.array([1080])             # IDs for Th-232 (90)
u233_id = np.array([1095])              # ID for U-233 (92)
pa233_id = np.array([1088])             # ID for Pa-233 (91)
# Volatile gases, interval 20 sec
kr_id = np.arange(217, 240)           # IDs for all isotopes of Kr(36)
xe_id = np.arange(718, 746)           # IDs for all isotopes of Xe(54)
# Noble metals, interval 20 sec
se_id = np.arange(175, 196)           # IDs for Selenium (34)
nob1_id = np.arange(331, 520)           # All elements from Nb(41) to Ag (47)
nob2_id = np.arange(636, 694)           # All elements from Sb(51) to Te (52)
noble_id = np.hstack((se_id, nob1_id, nob2_id))  # Stack all Noble Metals
# Seminoble metals, interval 200 days
zr_id = np.arange(312, 331)           # IDs for Zr (40)
semin_id = np.arange(520, 636)           # IDs from Cd(48) to Sn(50)
se_noble_id = np.hstack((zr_id, semin_id))  # Stack all Semi-Noble Metals
# Volatile fluorides, 60 days
br_id = np.arange(196, 217)           # IDs for Br(35)
i_id = np.arange(694, 718)           # IDs for I(53)
vol_fluorides = np.hstack((br_id, i_id))      # Stack volatile fluorides
# Rare earth, interval 50 days
y_id = np.arange(283, 312)           # IDs for Y(39)
rees_1_id = np.arange(793, 916)           # IDs for La(57) to Sm(62)
gd_id = np.arange(934, 949)           # IDs for Gd(64)
# Stack of all Rare earth except Eu
rees_id = np.hstack((y_id, rees_1_id, gd_id))
# Eu(63)
eu_id = np.arange(916, 934)
# Discard, 3435 days
rb_sr_id = np.arange(240, 283)        # Rb(37) and Sr(38) vector
cs_ba_id = np.arange(746, 793)        # Cs(55) and Ba(56) vector
# Stack discard
discard_id = np.hstack((rb_sr_id, cs_ba_id))
# Higher nuclides (Np-237 and Pu-242), interval 16 years (5840 days)
np_id    = np.array ([1109])         # 237Np93
pu_id    = np.array ([1123])         # 242Pu94
higher_nuc = np.hstack((np_id, pu_id))

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


def read_res(inp_filename, moment):
    """ Reads the .res file generated from serpent using PyNE

    Parameters:
    -----------
    inp_filename: str
        filename
    moment: int
        moment of depletion step (0 for BOC and 1 for EOC)

    Returns:
    --------
    [mean_keff, uncertainty_keff]
    """
    res_filename = os.path.join(inp_filename + "_res.m")
    res = serpent.parse_res(res_filename)
    keff_analytical = res['IMP_KEFF']
    return keff_analytical[moment]


def read_bumat(file_name, moment):
    """ Reads the .bumat file generated from serpent

    Parameters:
    -----------
    file_name: str
        name of file
    moment: int
        moment of depletion step (0 for BOC and 1 for EOC)

    Returns:
    --------
    dep_dict: dictionary
        key: isotope name
        val: adens
    material_def: str
        SERPENT material definition line
    """
    bumat_filename = os.path.join(file_name + ".bumat" + str(moment))
    dep_dict = {}
    with open(bumat_filename, 'r') as data:
        for line in itertools.islice(
                data, 5, 6):    # Read material description in variable
            material_def = line.strip()
        for line in itertools.islice(
                data, 0, None):  # Skip file header start=6, stop=None
            p = line.split()
            iso_name = nucname.name(p[0].split[0])
            adens = p[1]
            dep_dict[iso_name] = adens
    return dep_dict, material_def

def write_mat_file(file_name, dep_dict, fuel_intro, current_step):
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

#!!!!!! FIX !!!!!!#
def run_serpent(input_filename, cores):
    """ Runs the SERPENT input file using defined number of cores

    Parameters:
    -----------
    input_filename: str
        path to input file
    cores: int
        number of cores used to run SERPENT

    Returns:
    --------
    null. Runs SERPENT
    """
    if bw == 'True':
        args = (
            "aprun",
            "-n",
            str(nodes),
            "-d",
            str(32),
            "/projects/sciteam/bahg/serpent30/src/sss2",
            "-omp",
            str(32),
            input_filename)
    else:
        args = (
            "/home/andrei2/serpent/serpent2/src_test/sss2",
            "-omp",
            str(cores),
            input_filename)
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    print popen.stdout.read()

# Keep isotope atomic density constant and store cumulitive values into
# the TANK array


def pa_remove(target_isotope, removal_eff, bu_adens):
    """ Removes the target isotopes with the removal efficiency

    Parameters:
    -----------
    target_isotope: list
        list of target isotopes
    removal_eff: float
        removal efficiency
    bu_adens: array
        adens array

    Returns:
    --------
    bu_adens: array
        adens array after reprocessing
    tank_adens: array
        adens of wate stream
    """

    tank_adens = np.zeros(len(bu_adens))
    for i in target_isotope:
        # Store cumulitive adens of isotope in the end of step in tank
        tank_adens[i] = bu_adens[i] - (1 - removal_eff) * bu_adens[i]
        bu_adens[i] = (1 - removal_eff) * bu_adens[i]
    return bu_adens, tank_adens


def refill(refill_isotope, delta_adens, bu_adens):
    """ Refills the isotope by delta_adens

    Parameters:
    -----------
    refill_istope: array
        array with index of isootope to refill
    delta_adens: float
        admount of isotpe to add
    bu_adens:  array
        adens array

    Returns:
    --------
    bu_adens: array
        array with filled isotope
    """
    for i in refill_isotope:
        bu_adens[i] = bu_adens[i] + delta_adens
    return bu_adens

# Adding isotope to keep ADENs equal constant target_adens


def maintain_const(target_isotope, target_adens, bu_adens):
    """ Refills the isotope to keep its adens constant

    Parameters:
    -----------
    target_isotope: array
        array with index of isotope
    target_adens: float
        amount to refill the adens to
    bu_adens: array
        adens array

    Returns:
    --------
    bu_adens: array
        adens array
    tank_adens: array
        adens of waste stream 
    """
    tank_adens = np.zeros(len(bu_adens))
    for i in target_isotope:
        # Store cumulitive adens of isotope in the end of step in tank
        tank_adens[i] = bu_adens[i] - target_adens
        bu_adens[i] = target_adens
    return bu_adens, tank_adens


def main():
    if restart == 'True' and os.path.isfile(mat_file) is True:
        f = h5py.File(db_file, 'r+')
        keff_db = f['keff_EOC']
        keff_db_0 = f['keff_BOC']
        bu_adens_db_0 = f['core adensity before reproc']
        bu_adens_db_1 = f['core adensity after reproc']
        tank_adens_db = f['tank adensity']
        noble_adens_db = f['noble adensity']
        th_adens_db = f['Th tank adensity']
        isolib_db = f['iso_codes']
        keff = keff_db[0, :]  # Numpy array size [steps] containing Keff values
        isolib = isolib_db
        # Find last non-zero element in Keff array
        lasti = np.amax(np.nonzero(keff)) + 1
        print('Restaring simulation from step #' + str(lasti) +
              ' to step #' + str(lasti + steps) + '...')
        # Resize datasets
        keff_db.resize((2, steps + lasti))
        keff_db_0.resize((2, steps + lasti))
        bu_adens_db_0.resize((steps + lasti + 1, len(isolib)))
        bu_adens_db_1.resize((steps + lasti + 1, len(isolib)))
        tank_adens_db.resize((steps + lasti + 1, len(isolib)))
        noble_adens_db.resize((steps + lasti + 1, len(isolib)))
        th_adens_db.resize((steps + lasti + 1, len(isolib)))
        rem_adens = np.zeros((5, len(isolib)))
        # store Th-232 adens for 0 cycle
        th232_adens_0 = bu_adens_db_0[0, th232_id]
    else:
        # Create startup composition material file from the template
        shutil.copy('fuel_comp_with_fix', mat_file)
        lasti = 0
    for i in range(lasti + 1, lasti + steps + 1):
        # Run sss with initial fuel composition
        run_serpent(sss_input_file, cores)
        # Read depleted composition
        dep_dict, mat_def = read_bumat(sss_input_file, 1)
        isotope_list = list(dep_dict.keys())
        num_isotopes = len(dep_dict)
        if i == 1:   
            # Create HDF5 database if it's the first run
            f = h5py.File(db_file, "w")
            maxshape = (None, num_isotopes)

            # keff dbs are 2 shaped because they just have mean value and uncertainty
            keff_db = f.create_dataset('keff_EOC', (2, steps), 
                                       maxshape, chunks=True)
            keff_db_0 = f.create_dataset('keff_BOC', (2, steps),
                                         maxshape, chunks=True)

            # this shape encapsulates the entire isotopes vectors traced
            shape = (steps + 1, num_isotopes)
            bu_adens_db_0 = f.create_dataset('core adensity before reproc',shape,
                                             maxshape, chunks=True)
            bu_adens_db_1 = f.create_dataset('core adensity after reproc', shape,
                                             maxshape, chunks=True)
            tank_adens_db = f.create_dataset('tank adensity', shape,
                                             maxshape, chunks=True)
            noble_adens_db = f.create_dataset('noble adensity', shape,
                                              maxshape, chunks=True)
            th_adens_db = f.create_dataset('Th tank adensity', shape,
                                           maxshape, chunks=True)

            # !!!! WHATI S THIS #
            rem_adens = np.zeros((5, num_isotopes))
            dt = h5py.special_dtype(vlen=str)
            isolib_db = f.create_dataset('iso_codes', (num_isotopes,), dtype=dt)

            # Store ADENS, materials IDS for index=0
            db_0, mat_def = read_bumat(sss_input_file, 0)
            ### !!!!! SHOULDNT THIS BE 1?###
            ### !!! this looks wrong #
            db_1, mat_def = read_bumat(sss_input_file, 0)
            isolib_db[:] = isolib[:]
            # store Th-232 adens for 0 cycle
            th232_adens_0 = bu_adens_db_0[0, th232_id]
        else:
            f = h5py.File(db_file, 'r+')
            keff_db = f['keff_EOC']
            keff_db_0 = f['keff_BOC']
            bu_adens_db_0 = f['core adensity before reproc']
            bu_adens_db_1 = f['core adensity after reproc']
            tank_adens_db = f['tank adensity']
            noble_adens_db = f['noble adensity']
            th_adens_db = f['Th tank adensity']
            isolib_db = f['iso_codes']
        # Apply online reprocessing conditions
        # Store core composition before any removals and additions
        bu_adens_db_0[i, :] = bu_adens_arr
        # Keep Pa-233 concentration const and =0 and store cumulitive adens for
        # isotope in tank for Pa decay, interval 3days
        bu_adens_arr, tank_adens_db[i, ] = pa_remove(pa_id, 1, bu_adens_arr, i, 1)  # Removing interval=1step
        # Add U-233 from protactinium decay tank, rate = rate of Pa-233
        # removal, interval=3days=1step
        bu_adens_arr = refill(u233_id, tank_adens_db[i, pa233_id], bu_adens_arr)
        # Remove of Volatile Gases, Noble Metals (interval=3days)

        bu_adens_arr, rem_adens[0, ] = pa_remove(np.hstack((kr_id, xe_id, noble_id)),
                                                 1, bu_adens_arr)  # Every 1 step=3days
        # Remove seminoble metals, interval 200d=>67steps=201days
        if current_step % 67 == 0:
            bu_adens_arr, rem_adens[1, ] = pa_remove(np.hstack((se_noble_id)),
                                                     1, bu_adens_arr)  # Every 67steps=201days
        # Remove Volatile Fluorides every 60d=20steps
        if current_step % 20 == 0:
            bu_adens_arr, rem_adens[2, ] = pa_remove(np.hstack((vol_fluorides)),
                                                     1, bu_adens_arr)  # Every 20steps=60days
        # Remove REEs every 50days~51days=17steps
        if current_step % 17 == 0:
            bu_adens_arr, rem_adens[3, ] = pa_remove(np.hstack((rees_id)),
                                                     1, bu_adens_arr)  # Every 16steps=51days
        # Remove Eu every 500days~501days=167steps
        if current_step % 167 == 0:
            bu_adens_arr, rem_adens[4, ] = pa_remove(np.hstack((eu_id)),
                                                     1, bu_adens_arr)  # Every 167steps=501days
        # Remove Rb, Sr, Cs, Ba every 3435 days= 1145 steps
        if current_step % 1145 == 0:
            bu_adens_arr, rem_adens[4, ] = pa_remove(np.hstack((discard_id)),
                                                     1, bu_adens_arr)  # Every 1145 steps
        # Remove Np-237 and Pu-242 every 16 years = 5840 days= 1946 steps
        if current_step % 1946 == 0:                                                              
            bu_adens_arr, rem_adens[4, ] = pa_remove(np.hstack((higher_nuc)),
                                                     1, bu_adens_arr)
        # Refill Th-232 to keep ADENS const
        # Store rate of removal of Th-232[barn/cm3] and keep it adens in the
        # core constant
        bu_adens_arr, th_adens_db[i, ] = maintain_const(th232_id, th232_adens_0, bu_adens_arr)
        # Write input file with new materials ADENS
        write_mat_file(mat_file, isolib, bu_adens_arr, mat_def, i)

        # Print out what's going on
        print('Cycle number %s of %s steps' % (i, steps + lasti))
        # Write K_eff, core composition, Pa decay tank composition, noble gases
        # tank composition in database
        keff_db[:, i - 1] = read_res(sss_input_file, 1)
        keff_db_0[:, i - 1] = read_res(sss_input_file, 0)
        bu_adens_db_1[i, :] = bu_adens_arr
        tank_adens_db[i, :] = tank_adens_db[i - 1, :] + tank_adens_db[i, :]
        noble_adens_db[i, :] = noble_adens_db[i - 1, :] + rem_adens.sum(axis=0)
        th_adens_db[i,th232_id] =( th_adens_db[i - 1,th232_id] -
                                  (bu_adens_db_0[0,th232_id] - bu_adens_db_0[i,th232_id]) ) # Store amount of Th in tank
        # Save detector data in file
        #shutil.copy('core_det0.m', 'det/core_det_'+str(i))
        f.close()  # close DB


if __name__ == "__main__":
    main()
