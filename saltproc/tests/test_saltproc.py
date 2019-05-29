from __future__ import absolute_import, division, print_function
from saltproc import Depcode

import numpy as np
import pytest
import collections
import sqlite3 as lite
import h5py
import os
import argparse
import sys
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))


# global class object
directory = os.path.dirname(path)

serpent = Depcode(codename='SERPENT',
                  exec_path='/home/andrei2/serpent/serpent2/src_2131/sss2',
                  template_fname=directory+'/test',
                  input_fname=directory+'/test',
                  output_fname='NONE',
                  iter_matfile=directory+'/material')


def test_get_tra_or_dec():
    serpent.get_tra_or_dec()
    # print(serpent.iso_map)
    assert serpent.iso_map[380880] == '38088.09c'
    assert serpent.iso_map[962400] == '96240.09c'
    assert serpent.iso_map[952421] == '95342.09c'
    assert serpent.iso_map[340831] == '340831'
    assert serpent.iso_map[300732] == '300732'
    assert serpent.iso_map[511262] == '511262'
    assert serpent.iso_map[420931] == '420931'
    assert serpent.iso_map[410911] == '410911'
