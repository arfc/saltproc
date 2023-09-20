from pathlib import Path
import argparse
import json

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
neutron_paths = Path(f'{XSDIR}/neutrons').resolve().glob('**/*')

decay_files = [openmc.data.endf.Evaluation(str(x)) for x in decay_paths if x.is_file()]
nfy_files = [openmc.data.endf.Evaluation(str(x)) for x in nfy_paths if x.is_file()]
neutron_files = [str(x) for x in neutron_paths if x.is_file()]

fpy_files = nfy_files

endfb71_chain = Chain.from_endf(decay_files, fpy_files, neutron_files)
with open('branching_ratios_pwr.json') as f:
    br = json.load(f)
endfb71_chain.set_branch_ratios(br, strict=False)
endfb71_chain.export_to_xml('chain_endfb71_ace.xml')



