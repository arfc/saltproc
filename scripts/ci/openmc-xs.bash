#!/bin/bash
set -ex

wget -q -O - https://anl.box.com/shared/static/9igk353zpy8fn9ttvtrqgzvw1vtejoz6.xz | tar -C $HOME -xJ
mv $HOME/endfb-vii.1-hdf5 $HOME/endfb71_hdf5
