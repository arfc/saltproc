#!/usr/bin/python
"""Dakota-Saltproc Coupling Tool
================================

This script allows the user to find the optimum designs for optimal
entrainment separator efficiency of molten salt breeder reactor. The
script modifies saltproc input files (dot and json) and puts the results
into results.cvs file.

The main script dependencies \n
'os'
'subprocess'\n
'pandas'\n
'tables'\n
'numpy'\n
'dakota'\n
'json'\n
'saltproc'\n
be installed within the Python environment you are running this script in.

To run the dakota code and start to make sensitivity analysis,
use following command:

dakota -i msbr_dakota.in -o outputs/msbr_dakota.out > outputs/msbr_dakota.stdout

Notes
-----
Change the following paramaters according to where your codes are:
    'command' for path to saltproc code

"""


import dakota.interfacing as di
import subprocess
import json
import tables as tb
import numpy as np
import pandas as pd
import os


#  Constants for entrainment separator efficiency
eps_es = 0.95
T = 900
R = 8.31446261815324e3

T_ref = 700 + 273.15
Kc_xe = 0.057e-3
H_xe = R * T_ref * 1/Kc_xe

Kc_kr = 0.283e-3
H_kr = R * T_ref * 1/(Kc_kr)

Kc_h = 3.87e-3
H_h = R * T_ref * 1/Kc_h

d = 0.4
A_C = np.pi * (d/2)**2
L = 11.1
Q_L = 2.0
Q_He = 0.1
d_b = 0.508e-3


def eps(H, K_L):
    "Calculates entrainment separator efficiency"

    K_L = 0.3048 * K_L / 3600
    a = (6/d_b) * (Q_He / (Q_He + Q_L))
    alpha = (R*T*Q_L) / (H*Q_He)
    beta = (K_L*a*A_C*L*(1+alpha)) / Q_L

    return (1-np.exp(-beta))/(1+alpha)


if __name__ == '__main__':

    subprocess.run('mkdir outputs', shell=True)
    saltproc_path = '/path/to/saltproc/saltproc'

    #  Saltproc input/output files for editing
    work_dir = os.getcwd() + '/'
    inp_dir = work_dir + 'inputs/'
    out_dir = work_dir + 'outputs/'
    main_input = 'msbr_main.json'
    object_input = 'msbr_objects.json'
    results_file = 'msbr_results.csv'

    #  Variables for saltproc main input file
    node = 1
    processor = 6
    power_rampup_rate = 0  # percent per minute
    power_ramp = np.linspace(1e-10, 2250000000, 10, endpoint=False)
    depletion_step = 25  # in days
    cumulative_time = np.linspace(0.5, 12.5, depletion_step) / 24
    reactor_power = [1e-10 for i in range(15)]
    reactor_power = np.append(reactor_power, [2250000000 for i in range(10)])

    #  Import parameters from dakota
    params, results = di.read_parameters_file()

    #  Read json files
    with open(inp_dir + 'msbr_main.json') as main_file:
        main_data = json.load(main_file)
    with open(inp_dir + 'msbr_objects.json') as obj_file:
        object_data = json.load(obj_file)

    #  Edit saltproc input files with parameters
    main_data["Path output data storing folder"] = "outputs/"
    main_data["Number of neutrons per generation"] = 500
    main_data["Number of active generations"] = 60
    main_data["Number of inactive generations"] = 30
    main_data["Depletion step interval or Cumulative time (end of step) (d)"
              ] = cumulative_time.tolist()
    main_data["Reactor power or power step list during depletion step (W)"
              ] = reactor_power.tolist()
    output = ("msbr_%s_e%s.h5" % ("bol", int(params["K_L"])))
    main_data["Output HDF5 database file name"] = output

    #  Entrainment separator efficiency
    object_data["fuel"]["extraction_processes"
                        ]["entrainment_separator"]["efficiency"]["Kr"] =\
        eps(H_kr, params["K_L"]) * eps_es
    object_data["fuel"]["extraction_processes"
                        ]["entrainment_separator"]["efficiency"]["Xe"] =\
        eps(H_xe, params["K_L"]) * eps_es
    object_data["fuel"]["extraction_processes"
                        ]["entrainment_separator"]["efficiency"]["H"] =\
        eps(H_h, params["K_L"]) * eps_es

    #  Write data to json files
    with open(work_dir + 'msbr_main.json', 'w') as main_file:
        json.dump(main_data, main_file)
    with open(work_dir + 'msbr_objects.json', 'w') as obj_file:
        json.dump(object_data, obj_file)

    #  Simulate saltproc
    # command = 'python /path/to/saltproc/saltproc -i' + main_input
    command = 'python ' + saltproc_path + ' -n %i -d %i' % (node, processor) +\
              ' -i ' + work_dir + main_input
    subprocess.run(command, shell=True)

    #  Extract output parameters from h5 file
    db = tb.open_file(out_dir+output, mode='r')
    sim_param = db.root.simulation_parameters
    #  keff at the beginning of depletion step
    k_bds = np.array([x['keff_bds'][0] for x in sim_param.iterrows()])
    k_bds_err = np.array([x['keff_bds'][1] for x in sim_param.iterrows()])
    #  keff at the end of depletion step
    k_eds = np.array([x['keff_eds'][0] for x in sim_param.iterrows()])
    k_eds_err = np.array([x['keff_eds'][1] for x in sim_param.iterrows()])
    #  beta_eff at the end of depletion step
    b_eff_eds = np.array([x['beta_eff_eds'][0] for x in sim_param.iterrows()])
    #  breeding ratio
    br_ratio = np.array([x['breeding_ratio'][0] for x in sim_param.iterrows()])
    br_ratio_err = np.array([x['breeding_ratio'][1]
                            for x in sim_param.iterrows()])

    #  Write results to a file
    step = len(k_bds)
    data = {'dep_step': [i+1 for i in range(step)],
            'k_l': [params["K_L"] for i in range(step)],
            'k_bds': k_bds, 'k_bds_err': k_bds_err,
            'k_eds': k_eds, 'k_eds_err': k_eds_err,
            'b_eff_eds': b_eff_eds[:, 0],
            'b_eff_eds_err': b_eff_eds[:, 1],
            'br_ratio': br_ratio,
            'br_ratio_err': br_ratio_err}
    saltprocdata = pd.DataFrame(data)

    #  Read existing and write results to a file
    if os.path.isfile(results_file):
        saltprocdata.to_csv(results_file, sep='\t', mode='a',
                            header=False, index=False)
    else:
        saltprocdata.to_csv(results_file, sep='\t', mode='w',
                            header=True, index=False)

    #  Responses also can be accessed by descriptor or index
    results["obj_fn_1"].function = k_bds[step-1]
    results["obj_fn_2"].function = k_bds_err[step-1]
    results["obj_fn_3"].function = k_eds[step-1]
    results["obj_fn_4"].function = k_eds_err[step-1]
    results["obj_fn_5"].function = b_eff_eds[step-1, 0]
    results["obj_fn_6"].function = b_eff_eds[step-1, 1]
    results["obj_fn_7"].function = br_ratio[step-1]
    results["obj_fn_8"].function = br_ratio_err[step-1]
    results.write()

    db.close()
