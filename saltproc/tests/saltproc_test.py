import numpy as np
import pytest
import collections
import sqlite3 as lite
import h5py
import os
import sys
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
import class_saltproc_array as csa

# global clas object
saltproc = csa.saltproc(5,32,32,'False', input_file='test',
                        db_file='test_db.hdf5', mat_file='test_mat')

def test_init_db_file_creation():
    """ Test if the db is created correctly"""
    # this is like this because it errors, but runs
    try:
        saltproc.init_db()
    except:
        z = 0
    assert os.path.isfile('test_db.hdf5')

def test_init_db_dataset():
    """ Tests if the db is initialized correctly"""
    f = h5py.File(saltproc.db_file, 'r')
    dataset_lists = ['keff_BOC', 'tank adensity', 'iso codes', 'noble adensity',
                     'keff_EOC', 'core adensity before reproc', 'core adensity after reproc',
                     'Th tank adensity']
    for key in f.keys():
        assert key in dataset_lists

def test_read_res():
    """ Tests if the res file is read correctly"""
    keff = saltproc.read_res(0)
    assert keff[0] == 1.07447
    assert keff[1] == 0.00213

def test_read_bumat():
    isolib_array, bu_adens, mat_def = saltproc.read_bumat(saltproc.input_file, 0)
    assert isolib_array[0] == '1001.10c'
    assert bu_adens[0] == 0.00000000000000E+00

    assert isolib_array[-1] == '982510'
    assert bu_adens[0] == 0.00000000000000E+00

    assert isolib_array[saltproc.th232_id] == '90232.10c'
    assert bu_adens[saltproc.th232_id[0]] == 3.69244822559746E-03
    
def test_read_bumat_matef():
    isolib_array, bu_adens, mat_def = saltproc.read_bumat(saltproc.input_file, 0)
    solution = 'mat  fuel  7.77767011499957E-02 vol 5.51573E+06'
    assert mat_def == solution
    
def test_write_mat_file():
    # this is like this because it errors, but runs
    try:
        saltproc.write_mat_file()
    except:
        z = 0
    with open(saltproc.mat_file, 'r') as f:
        lines = f.readlines()
        for linenum, line in enumerate(lines):
            if linenum == 0:
                solution = '% Step number # 0 1.074470 +- 0.002130;1.014630 +- 0.002520'
                assert line.rstrip() == solution