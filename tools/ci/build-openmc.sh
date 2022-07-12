#!/bin/bash
set -ex

# Build openmc
cd openmc
python tools/ci/gha-install.py

# Create the caching folder
mkdir openmc_src
mkdir openmc_src/bin
mkdir openmc_src/lib
mkdir openmc_src/share
mkdir openmc_src/include

# Copy libraries to caching folder
cp /usr/local/bin/openmc openmc_src/bin/.
cp /usr/local/lib/libopenmc.so openmc_src/lib/.
cp -r /usr/local/lib/cmake openmc_src/lib/.
cp /usr/local/lib/libpugixml.a openmc_src/lib/.
cp -r /usr/local/lib/pkgconfig openmc_src/lib/.
cp -r /usr/local/share/openmc openmc_src/share/.
cp -r /usr/local/share/man openmc_src/share/.
cp -r /usr/local/include/openmc openmc_src/include/.
cp /usr/local/include/pugiconfig.hpp openmc_src/include/.
cp /usr/local/include/pugixml.hpp openmc_src/include/.
cp -r /usr/local/include/fmt openmc_src/include/.
cp -r /usr/local/include/xtl openmc_src/include/.
cp -r /usr/local/include/xtensor openmc_src/include/.
cp -r /usr/local/include/gsl openmc_src/include/.
cp -r /usr/local/include/gsl-lite openmc_src/include/.

# Move the caching folder to $HOME
mv openmc_src $HOME/openmc_src

# Install the OpenMC python API
pip install .
cd ../
