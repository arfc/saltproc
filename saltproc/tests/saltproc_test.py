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
from saltproc import saltproc

# global class object
directory = os.path.dirname(path)

saltproc = saltproc(5, 1, 32, 'False',
                    exec_path='/projects/sciteam/bahg/serpent30/src/sss2',
                    restart=False,
                    input_file=directory+'/test',
                    db_file=directory+'/test_db.hdf5',
                    init_mat_file=directory+'/test_mat',
                    blanket_mat_name='blank',
                    rep_scheme={'he': {'element': ['He'],
                                       'from': 'fuel'}})

try:
    os.remove(directory+'/test_db.hdf5')
except:
    z = 1


def test_init_db_file_creation():
    """ Test if the db is created correctly"""
    # this is like this because it errors, but runs
    saltproc.init_db()
    assert os.path.isfile(directory+'/test_db.hdf5')


def test_init_db_dataset():
    """ Tests if the db is initialized correctly"""
    f = h5py.File(saltproc.db_file, 'r')
    dataset_lists = ['keff_BOC',
                     'driver composition before reproc',
                     'driver composition after reproc',
                     'driver refill tank composition',
                     'blanket composition before reproc',
                     'blanket composition after reproc',
                     'blanket refill tank composition',
                     'fissile tank composition',
                     'waste tank composition',
                     'iso names',
                     'iso zai',
                     'siminfo_timestep',
                     'siminfo_pop',
                     'siminfo_totsteps']
    print(list(f.keys()))
    for dataset in dataset_lists:
        assert dataset in list(f.keys())


def test_read_res():
    """ Tests if the res file is read correctly"""
    keff = saltproc.read_res(0)
    assert keff[0] == 1.07447
    assert keff[1] == 0.00213

    keff = saltproc.read_res(1)
    assert keff[0] == 1.01463
    assert keff[1] == 0.00252


def test_read_dep():
    dep_dict = saltproc.read_dep()
    assert dep_dict['fuel'][0] == 1.32023e-09

    assert dep_dict['fuel'][-1] == 0

    assert dep_dict['blank'][0] == 1.31815e-09


def test_get_mat_def():
    mat_def = saltproc.get_mat_def()
    solution = 'mat  fuel  7.77767011499957E-02 fix 10c 1000 burn 1 vol 4.87100E+07 '
    print(saltproc.mat_def_dict)
    assert saltproc.mat_def_dict['fuel'] == solution


def test_write_mat_file():
    # this is like this because it errors, but runs
    saltproc.read_dep()
    saltproc.get_mat_def()
    saltproc.separate_fuel()
    saltproc.write_mat_file()
    z = 0
    with open(saltproc.mat_file, 'r') as f:
        lines = f.readlines()
        for linenum, line in enumerate(lines):
            if linenum == 0:
                solution = ('% Step number # 0 1.074470 +- 0.002130;'
                            '1.014630 +- 0.002520')
                assert line.rstrip() == solution


def test_get_isos():
    saltproc.get_isos()
    assert len(saltproc.isoname) == 1715
    assert len(saltproc.isozai) == 1715
    assert saltproc.isoname[-1] == 'Bk251'
    assert saltproc.isoname[0] == 'H1'
    assert saltproc.isozai[0] == 10010
    assert saltproc.isozai[-1] == 972510


def test_find_iso_indx_iso():
    saltproc.get_isos()
    indx = saltproc.find_iso_indx('Bk251')
    assert indx[0] == 1714
    indx = saltproc.find_iso_indx('H1')
    assert indx[0] == 0


def test_find_iso_indx_el():
    saltproc.get_isos()
    indx = saltproc.find_iso_indx(['H'])
    assert all(indx == [0, 1, 2])
    indx = saltproc.find_iso_indx(['Cm'])
    assert indx[0] == 343
    assert indx[-1] == 1713


def test_get_library_isotopes():
    saltproc.get_library_isotopes()
    print(saltproc.lib_isos)
    assert saltproc.lib_isos[0] == '89225.09c'
    assert saltproc.lib_isos[-1] == '40096.10c'


def test_rep_scheme_init():
    print(saltproc.rep_scheme)
    assert saltproc.rep_scheme['he']['to'] == 'waste'
    assert saltproc.rep_scheme['he']['freq'] == -1
    assert saltproc.rep_scheme['he']['qty'] == -1
    assert saltproc.rep_scheme['he']['begin_time'] == -1
    assert saltproc.rep_scheme['he']['end_time'] == 1e+299
    assert saltproc.rep_scheme['he']['eff'] == 1
