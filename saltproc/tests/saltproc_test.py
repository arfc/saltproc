import numpy as np
import pytest
import collections
import sqlite3 as lite
import h5py
import os
import sys
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
from saltproc import saltproc


# global clas object
directory = os.path.dirname(path)
saltproc = saltproc(5, 32, 32, 'False', restart=False,
                    input_file=directory+'/test',
                    db_file=directory+'/test_db.hdf5',
                    mat_file=directory+'/test_mat')
os.remove(directory+'/test_db.hdf5')

def test_init_db_file_creation():
    """ Test if the db is created correctly"""
    # this is like this because it errors, but runs
    saltproc.init_db()
    assert 1 ==2
    assert os.path.isfile(directory+'/test_db.hdf5')


def test_init_db_dataset():
    """ Tests if the db is initialized correctly"""
    f = h5py.File(saltproc.db_file, 'r')
    dataset_lists = ['keff_BOC', 'tank adensity', 'iso codes',
                     'noble adensity', 'keff_EOC',
                     'core adensity before reproc',
                     'core adensity after reproc',
                     'Th tank adensity']
    for key in f.keys():
        assert key in dataset_lists


def test_read_res():
    """ Tests if the res file is read correctly"""
    keff = saltproc.read_res(0)
    assert keff[0] == 1.07447
    assert keff[1] == 0.00213


def test_read_bumat():
    bumat_dict, mat_def = saltproc.read_bumat(
        saltproc.input_file, 0)
    assert bumat_dict['H1'] == 0.00000000000000E+00

    assert bumat_dict['Cf251'] == 0.00000000000000E+00

    assert bumat_dict['Th232'] == 3.69244822559746E-03
    assert 1 ==2


def test_read_bumat_matef():
    bumat_dict, mat_def = saltproc.read_bumat(
        saltproc.input_file, 0)
    solution = 'mat  fuel  7.77767011499957E-02 vol 5.51573E+06'
    assert mat_def == solution


def test_write_mat_file():
    # this is like this because it errors, but runs
    saltproc.bumat_dict, saltproc.mat_def = saltproc.read_bumat(
        saltproc.input_file, 0)
    saltproc.process_fuel()
    saltproc.write_mat_file()
    z = 0
    with open(saltproc.mat_file, 'r') as f:
        lines = f.readlines()
        for linenum, line in enumerate(lines):
            if linenum == 0:
                solution = ('% Step number # 0 1.074470 +- 0.002130;'
                           '1.014630 +- 0.002520')
                assert line.rstrip() == solution


def test_process_fuel():
    saltproc.process_fuel()
    assert saltproc.bu_adens_db_0[saltproc.current_step, 0] == pytest.approx(
        1.8811870e-09, 1e-6)
    assert saltproc.bu_adens_db_0[saltproc.current_step, 1] == pytest.approx(
        1.0529505e-10, 1e-7)


def test_process_th():
    th232_id = saltproc.find_iso_indx('Th232')
    saltproc.init_db()
    assert saltproc.th_adens_db[saltproc.current_step,
                                th232_id] == pytest.approx(-3.684984e-06, 1e-5)
