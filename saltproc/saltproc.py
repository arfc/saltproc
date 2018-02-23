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
restart        = 'False'                      # Restart option off by default
sss_input_file = 'core'                       # Serpent 2 file without fuel description and geometry
db_file        = 'db_saltproc.hdf5'           # HDF5 database name
#dep_file       =   'core_dep.m'              # Path and name depletion output from Serpent
#bumat_file     = 'core.bumat1'               # Path and name depletion output from Serpent
mat_file       =   'fuel_comp'                # Path and name of file with materials data (input for Serpent)
cores          =   32                         # Number of OMP cores to use
nodes          =   1                          # Number of nodes by defaule
bw             =  'False'                     # Not cluster by default
steps          =   5                          # 5 fuel cycle steps by default
# Isotopes description
pa_id          = np.array([1088])             # ID of isotope for which we want to keep constant adens (Pa-233, 232,234,235)
th232_id       = np.array([1080])             # IDs for Th-232 (90)
u233_id        = np.array([1095])             # ID for U-233 (92)
pa233_id       = np.array([1088])             # ID for Pa-233 (91)
# Volatile gases, interval 20 sec
kr_id          = np.arange(217,240)           # IDs for all isotopes of Kr(36)
xe_id          = np.arange(718,746)           # IDs for all isotopes of Xe(54)
# Noble metals, interval 20 sec
se_id          = np.arange(175,196)           # IDs for Selenium (34)
nob1_id        = np.arange(331,520)           # All elements from Nb(41) to Ag (47)
nob2_id        = np.arange(636,694)           # All elements from Sb(51) to Te (52)
noble_id       = np.hstack((se_id,nob1_id, nob2_id))# Stack all Noble Metals
# Seminoble metals, interval 200 days
zr_id          = np.arange(312,331)           # IDs for Zr (40)
semin_id       = np.arange(520,636)           # IDs from Cd(48) to Sn(50)
se_noble_id    = np.hstack((zr_id,semin_id))  # Stack all Semi-Noble Metals
# Volatile fluorides, 60 days
br_id          = np.arange(196,217)           # IDs for Br(35)
i_id           = np.arange(694,718)           # IDs for I(53)
vol_fluorides  = np.hstack((br_id,i_id))      # Stack volatile fluorides
# Rare earth, interval 50 days
y_id           = np.arange(283,312)           # IDs for Y(39)
rees_1_id      = np.arange(793,916)           # IDs for La(57) to Sm(62)
gd_id          = np.arange(934,949)           # IDs for Gd(64)
rees_id        = np.hstack((y_id, rees_1_id, gd_id)) # Stack of all Rare earth except Eu
# Eu(63)
eu_id          = np.arange(916,934)

# Parse flags
parser = argparse.ArgumentParser()
parser.add_argument('-r', choices=['True', 'False']) # Restart flag -r
parser.add_argument('-n', nargs=1, type=int, default=1)         # Number of nodes -n
parser.add_argument('-steps', nargs=1, type=int, default=5)     # Number of steps
parser.add_argument('-bw', choices=['True', 'False']) # -bw Blue Waters?
args = parser.parse_args()
restart = args.r
nodes   = int(args.n[0])
steps   = int(args.steps[0])
bw      = args.bw

# Read *.dep output Serpent file and store it in few arrays
def read_dep (inp_filename):
    dep_filename = os.path.join(inp_filename + "_res.m")
    dep = serpent.parse_dep(dep_filename, make_mats=False)
    days =    dep['DAYS']                        # Time array parsed from *_dep.m file
    time_step = np.diff(days)                    # Depletion time step evaluation
    isoid =  dep['ZAI']                          # Codes of isotopes parsed from *_dep.m file
    names = dep['NAMES']                         # Names of isotopes parsed from *_dep.m file
    EOC = np.amax(days)                          # End of cycle (simulation time length)
    iso_mass = dep['TOT_MASS']                   # Mass if each isotope in core
    adens_fuel = dep['MAT_fuel_ADENS']           # atomic density for each isotope in material 'fuel'
    mdens_fuel = dep['MAT_fuel_MDENS']           # mass density for each isotope in material 'fuel'
    vol_fuel   = dep['MAT_fuel_VOLUME']          # total volume of material 'fuel'
    #return (days, time_step, isonum, isosize)
    fuel_mass  = mdens_fuel[isoid.size-1,:]*vol_fuel              # Calculate total fuel mass
    return isoid, days, time_step, EOC, fuel_mass, iso_mass, adens_fuel[:,1], mdens_fuel[:,1], vol_fuel
# Read *.res output Serpent file and store it in few arrays
def read_res (inp_filename, moment):             # moment=0 for BOC and moment=1 for EOC
    res_filename = os.path.join(inp_filename + "_res.m")
    res = serpent.parse_res(res_filename)
    keff_analytical = res['IMP_KEFF']   
    return keff_analytical[moment,:] # Value Keff and uncertantly for the moment (two values in list: BOS and EOS)

# Read bumat# Serpent file and parse name of isotope, atomic density and general fuel description (material_def)
def read_bumat(file_name, moment):   #moment=0 for BoC, moment=1 for EoC
    bumat_filename = os.path.join(file_name + ".bumat" + str(moment))
    with open(bumat_filename, 'r') as data:
        isolib = []
        bu_adens = []
        material_def = []
        for line in itertools.islice(data, 5, 6):    # Read material description in variable
            material_def = line.strip()
        for line in itertools.islice(data, 0, None): # Skip file header start=6, stop=None
            p = line.split()
            isolib.append(str(p[0]))
            bu_adens.append(float(p[1]))
    isolib_array = np.asarray(isolib)
    #print isolib_array
    return isolib_array, bu_adens, material_def

# Write fuel introduction info and two columns (isoname and atomic density) in file
def write_mat_file(file_name, isolib, bu_adens, fuel_intro, current_step):
    ana_keff_boc = read_res(sss_input_file,0)
    ana_keff_eoc = read_res(sss_input_file,1)
    matf = open (file_name, 'w')
    matf.write ('% Step number #' + str(current_step) + '  ' + str(ana_keff_boc) +';'+str(ana_keff_eoc) + '\n')
    matf.write(fuel_intro + ' burn 1 rgb 253 231 37\n')
    for index in range(len(isolib)):
        matf.write(str(isolib[index]) + "        " + str(bu_adens[index]) + "\n")
    matf.close()
    
# Just run serpent with input file 'input_file' and using cores
def run_serpent (input_filename, cores):
    if bw == 'True':
	args = ("aprun", "-n", str(nodes), "-d", str(cores), "/projects/sciteam/bahg/serpent/src/sss2", "-omp", str(cores), input_filename)
    else:
    	args = ("/home/andrei2/serpent/serpent2/src_test/sss2", "-omp", str(cores), input_filename)
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    #popen.wait()
    #output = popen.stdout.read()
    print popen.stdout.read()
    
# Keep isotope atomic density constant and store cumulitive values into the TANK array
def pa_remove (target_isotope, removal_eff, bu_adens, current_step, removal_interval):
    tank_adens = np.zeros(len(bu_adens))
    if current_step % removal_interval == 0: # Check is it time to removing isotope? i.e. 5step/3step interval =2, NO
        for i in target_isotope:
            tank_adens[i] = bu_adens[i] - (1-removal_eff)*bu_adens[i]    # Store cumulitive adens of isotope in the end of step in tank
            bu_adens[i] = (1-removal_eff)*bu_adens[i]
        #print (target_isotope)
    return bu_adens, tank_adens

# Adding isotope with rate equal refill_rate[10e+24atoms/cm3 per cycle step]
def refill (refill_isotope, delta_adens, bu_adens):
    for i in refill_isotope:
        bu_adens[i] = bu_adens[i] + delta_adens
    return bu_adens
  
# Main run
def main():
    if restart == 'True' and os.path.isfile(mat_file) is True:
	f = h5py.File(db_file, 'r+')
	keff_db = f['keff']
 	bu_adens_db_0    = f['core adensity before reproc']
 	bu_adens_db_1    = f['core adensity after reproc']
        tank_adens_db  = f['tank adensity']
        noble_adens_db = f['noble adensity']
        th_adens_db    = f['Th tank adensity']
        isolib_db      = f['iso_codes']
	keff = keff_db[0,:] # Numpy array size [steps] containing Keff values
	isolib = isolib_db
	# Find last non-zero element in Keff array
	lasti = np.amax(np.nonzero(keff)) + 1
	print ('Restaring simulation from step #' + str(lasti) + ' to step #' + str(lasti+steps)+'...')
	# Resize datasets
	keff_db.resize((2, steps+lasti))
	bu_adens_db_0.resize   ((steps+lasti+1,len(isolib)))
	bu_adens_db_1.resize   ((steps+lasti+1,len(isolib)))
	tank_adens_db.resize ((steps+lasti+1,len(isolib)))
	noble_adens_db.resize((steps+lasti+1,len(isolib)))
	th_adens_db.resize   ((steps+lasti+1, len(isolib)))
        rem_adens     = np.zeros((5,len(isolib)))
        th232_adens_0 = bu_adens_db_0[0,th232_id] # store Th-232 adens for 0 cycle            
    else:
	# Create startup composition material file from the template
	shutil.copy('fuel_comp_with_fix', mat_file)
	lasti = 0
    for i in range(lasti+1,lasti+steps+1):
        # Run sss with initial fuel composition
        run_serpent (sss_input_file, cores)
        # Read bumat file
        isolib, bu_adens_arr, mat_def = read_bumat (sss_input_file,1)
        if i == 1:   # First run, create HDF5 dataset after 1st run
	    # Create HDF5 database
	    f    = h5py.File (db_file,"w")
	    keff_db = f.create_dataset ('keff', (2,steps), maxshape=(2,None),chunks=True)
            bu_adens_db_0 = f.create_dataset ('core adensity before reproc', (steps+1,len(isolib)), maxshape=(None,len(isolib)),chunks=True)
            bu_adens_db_1 = f.create_dataset ('core adensity after reproc', (steps+1,len(isolib)), maxshape=(None,len(isolib)),chunks=True)
            tank_adens_db = f.create_dataset ('tank adensity', (steps+1,len(isolib)), maxshape=(None,len(isolib)),chunks=True)
            noble_adens_db = f.create_dataset ('noble adensity', (steps+1,len(isolib)), maxshape=(None,len(isolib)),chunks=True)
            th_adens_db = f.create_dataset ('Th tank adensity', (steps+1,len(isolib)), maxshape=(None,len(isolib)),chunks=True)
            rem_adens = np.zeros((5,len(isolib)))
            dt = h5py.special_dtype(vlen=str)
            isolib_db    = f.create_dataset ('iso_codes', (len(isolib),), dtype=dt)
            # Store ADENS, materials IDS for index=0
            isolib, bu_adens_db_0[0,:], mat_def = read_bumat (sss_input_file,0)
	    isolib, bu_adens_db_1[0,:], mat_def = read_bumat (sss_input_file,0)
            isolib_db[:] = isolib[:]
            th232_adens_0 = bu_adens_db_0[0,th232_id]# store Th-232 adens for 0 cycle 
        # Apply online reprocessing conditions
	# Store core composition before any removals and additions
        bu_adens_db_0[i,:] = bu_adens_arr
        # Keep Pa-233 concentration const and =0 and store cumulitive adens for isotope in tank for Pa decay, interval 3days
        bu_adens_arr, tank_adens_db[i,]  = pa_remove (pa_id, 1, bu_adens_arr, i, 1) # Removing interval=1step
        # Add U-233 from protactinium decay tank, rate = rate of Pa-233 removal, interval=3days=1step
        bu_adens_arr = refill (u233_id, tank_adens_db[i,pa233_id], bu_adens_arr)
        # Remove of Volatile Gases, Noble Metals (interval=3days)
        bu_adens_arr, rem_adens[0,] = pa_remove (np.hstack((kr_id,xe_id,noble_id)), 1, bu_adens_arr, i, 1) # Every 1 step=3days
        # Remove seminoble metals, interval 200d=>67steps=201days
        bu_adens_arr, rem_adens[1,] = pa_remove (np.hstack((se_noble_id)), 1, bu_adens_arr, i, 67) # Every 67steps=201days
        # Remove Volatile Fluorides every 60d=20steps
        bu_adens_arr, rem_adens[2,] = pa_remove (np.hstack((vol_fluorides)), 1, bu_adens_arr, i, 20) # Every 20steps=60days
        # Remove REEs every 50days~51days=17steps
        bu_adens_arr, rem_adens[3,] = pa_remove (np.hstack((rees_id)), 1, bu_adens_arr, i, 17) # Every 16steps=51days
        # Remove Eu every 500days~501days=167steps
        bu_adens_arr, rem_adens[4,] = pa_remove (np.hstack((eu_id)), 1, bu_adens_arr, i, 167) # Every 167steps=501days
        # Refill Th-232 to keep ADENS const
        bu_adens_arr, th_adens_db[i,] = pa_remove (th232_id, th232_adens_0, bu_adens_arr, i, 1) # Store rate of removal of Th-232[barn/cm3]
        # Write input file with new materials ADENS   
        write_mat_file(mat_file, isolib,  bu_adens_arr, mat_def,i)

        # Print out what's going on
        print ('Cycle number %s of %s steps' % (i, steps+lasti))
        # Write K_eff, core composition, Pa decay tank composition, noble gases tank composition in database
        keff_db[:,i-1] = read_res(sss_input_file,1)
        bu_adens_db_1[i,:]  = bu_adens_arr
        tank_adens_db[i,:]  = tank_adens_db[i-1,:] + tank_adens_db[i,:]
        noble_adens_db[i,:] = noble_adens_db[i-1,:] + rem_adens.sum(axis=0)
	th_adens_db[i,th232_id]    = th_adens_db[i-1,th232_id] - (bu_adens_db_0[0,th232_id] - bu_adens_db_0[i, th232_id]) # Store amount of Th in tank

    f.close()	# close DB    

if __name__== "__main__":
    main()
