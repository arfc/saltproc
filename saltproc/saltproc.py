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

sss_input_file = 'core'                       # Serpent 2 file without fuel description and geometry
sss_exe        = '/home/andrei2/serpent/serpent2/src_omp/sss2'  # Serpent2 executable
#dep_file       =   'core_dep.m'              # Path and name depletion output from Serpent
#bumat_file     = 'core.bumat1'               # Path and name depletion output from Serpent
mat_file       =   'fuel_comp'                # Path and name of file with materials data (input for Serpent)
cores          =   4                          # Number of OMP cores to use
steps          =   2                          # Number of depletion steps needed
pa_id          = np.arange(1050,1054)         # ID of isotope for which we want to keep constant adens (Pa-233, 232,234,235)
kr_id          = np.arange(200,224)           # IDs for all isotopes of Kr(36)
xe_id          = np.arange(684,710)           # IDs for all isotopes of Xe(54)
th232_id       = np.array([1042])             # IDs for Th-232

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
    args = (sss_exe, "-omp", str(cores), input_filename)
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    #popen.wait()
    #output = popen.stdout.read()
    print popen.stdout.read()
    
# Keep isotope atomic density constant and store cumulitive values into the TANK array
def pa_remove (target_isotope, target_adens, bu_adens):
    tank_adens = np.zeros(len(bu_adens))
    for i in target_isotope:
        tank_adens[i] = bu_adens[i] - target_adens        # Store cumulitive adens of isotope in the end of step in tank
        bu_adens[i] = target_adens
    #print (target_isotope)
    #print tank_adens[198:225]
    return bu_adens, tank_adens
  
# Main run
def main():
    # Create startup composition material file from the template
    shutil.copy('fuel_comp_with_fix', 'fuel_comp')

    # Create HDF5 database
    f    = h5py.File ("saltproc_main.hdf5","w")
    keff_db = f.create_dataset ('keff', (2,steps+1))
    # First step run
    #run_serpent (sss_input_file, cores)
    #keff_db[:,0] = read_res(sss_input_file,0)   # store Keff for BoC
    #keff_db[:,1] = read_res(sss_input_file,1)   # store Keff for EoC
    # Read bumat file

    #bu_adens_db[0,:]  = bu_adens_init
    for i in range(1,steps+1):
        # Run sss with initial fuel composition
        run_serpent (sss_input_file, cores)
        # Read bumat file
        isolib, bu_adens_arr, mat_def = read_bumat (sss_input_file,1)
        if i == 1:   # First run, create HDF5 dataset after 1st run
            bu_adens_db   = f.create_dataset ('core adensity', (steps+1,len(isolib)))
            tank_adens_db = f.create_dataset ('tank adensity', (steps+1,len(isolib)))
            noble_adens_db = f.create_dataset ('noble adensity', (steps+1,len(isolib)))
            th_adens_db = f.create_dataset ('Th refill adensity', (steps+1,len(isolib)))
            dt = h5py.special_dtype(vlen=str)
            isolib_db    = f.create_dataset ('iso_codes', (len(isolib),), dtype=dt)
            keff_db[:,0] = read_res(sss_input_file,0)   # store Keff for BoC
            isolib, bu_adens_db[0,:], mat_def = read_bumat (sss_input_file,0)
            isolib_db[:] = isolib[:]
            th232_adens_0 = bu_adens_db[0,th232_id]# store Pa-232 adens for 0 cycle            
        # Apply online reprocessing conditions
        # Keep Pa-233 concentration const and =0 and store cumulitive adens for isotope in tank for Pa decay
        bu_adens_arr, tank_adens_db[i,]  = pa_remove (pa_id, 0, bu_adens_arr)
        bu_adens_arr, noble_adens_db[i,] = pa_remove (np.hstack((kr_id,xe_id)), 0, bu_adens_arr) # remove all Kr&Xe
        bu_adens_arr, th_adens_db[i,] = pa_remove (th232_id, th232_adens_0, bu_adens_arr)        # keep Th-232 concentration constant
        # Write input file with new materials ADENS   
        write_mat_file(mat_file, isolib,  bu_adens_arr, mat_def,i)

        # Print out what's going on
        print ('Cycle number %s of %s steps' % (i, steps))
        # Write K_eff in database
        keff_db[:,i] = read_res(sss_input_file,1)
        bu_adens_db[i,:] = bu_adens_arr
        tank_adens_db[i,:] = tank_adens_db[i-1,:] + tank_adens_db[i,:] 

    f.close()

if __name__== "__main__":
    main()
