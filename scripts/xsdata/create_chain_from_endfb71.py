from pathlib import Path
import argparse

import numpy as np
import pandas as pd
import openmc
from openmc.deplete import Chain
from openmc.data import zam, gnds_name

parser = argparse.ArgumentParser()
parser.add_argument('-D',
                    type=str,
                    help='XSDIR path')

args = parser.parse_args()
XSDIR = args.D


decay_paths = Path(f'{XSDIR}/decay').resolve().glob('**/*')
nfy_paths = Path(f'{XSDIR}/nfy').resolve().glob('**/*')
sfy_paths = Path(f'{XSDIR}/sfy').resolve().glob('**/*')
neutron_paths = Path(f'{XSDIR}/neutrons').resolve().glob('**/*')

decay_files = [openmc.data.endf.Evaluation(str(x)) for x in decay_paths if x.is_file()]
nfy_files = [openmc.data.endf.Evaluation(str(x)) for x in nfy_paths if x.is_file()]
sfy_files = [openmc.data.endf.Evaluation(str(x)) for x in sfy_paths if x.is_file()]
neutron_files = [str(x) for x in neutron_paths if x.is_file()]

fpy_files = nfy_files + sfy_files

branching_ratios = pd.read_csv('serpent_branching_ratios.csv', header=None).to_numpy()
endfb71_chain = Chain.from_endf(decay_files, fpy_files, neutron_files)
for nuc, ground_ratio, meta_ratio in branching_ratios:
    Z, A, M = zam(nuc)
    ground_nuc = gnds_name(Z, A+1, M)
    meta_nuc = gnds_name(Z, A+1, M+1)
    branch_ratios = {ground_nuc: float(ground_ratio),
                     meta_nuc: float(meta_ratio)}
    branch_ratios = {nuc: branch_ratios}
    endfb71_chain.set_branch_ratios(branch_ratios, '(n,gamma)')

endfb71_chain.export_to_xml('chain_endfb71_ace.xml')



