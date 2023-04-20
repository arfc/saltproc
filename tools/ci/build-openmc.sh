#!/bin/bash
set -ex

# Build openmc
cd openmc
./tools/ci/gha-install-mcpl.sh
python tools/ci/gha-install.py

# Create the caching folder
DIRS=(openmc_src mcpl_src)
for DIR in ${DIRS[@]}; do
    mkdir $DIR
    mkdir $DIR/bin
    mkdir $DIR/lib
    mkdir $DIR/share
    mkdir $DIR/include
done

# Copy libraries to caching folder
cp /usr/local/bin/openmc openmc_src/bin/.
cp /usr/local/lib/libopenmc.so openmc_src/lib/.
cp -r /usr/local/lib/cmake openmc_src/lib/.
cp /usr/local/lib/libpugixml.a openmc_src/lib/.
cp -r /usr/local/lib/pkgconfig openmc_src/lib/.
#cp -r /usr/local/share/openmc openmc_src/share/.
#cp -r /usr/local/share/man openmc_src/share/.
cp -r /usr/local/include/openmc openmc_src/include/.
cp /usr/local/include/pugiconfig.hpp openmc_src/include/.
cp /usr/local/include/pugixml.hpp openmc_src/include/.
INCLUDES=(fmt xtl xtensor gsl gsl-lite openmc)
for I in ${INCLUDES[@]}; do
    cp -r /usr/local/include/$I openmc_src/include/.
done

# MCPL stuff
cp /usr/local/lib/libmcpl.so mcpl_src/lib/.
cp /usr/local/include/mcpl.h mcpl_src/include/.
cp /usr/local/lib/libsswmcpl.so mcpl_src/lib/.
cp /usr/local/lib/libphitsmcpl.so mcpl_src/lib/.
cp -r /usr/local/share/MCPL mcpl_src/share/.

MCPL_BINARIES=(pymcpltool mcpl-config mcpl2ssw ssw2mcpl mcpl2phits phits2mcpl mcpltool)
for BINARY in ${MCPL_BINARIES[@]}; do
    cp /usr/local/bin/$BINARY mcpl_src/bin/.
done


# Move the caching folders to $HOME
mv openmc_src $HOME/openmc_src
mv mcpl_src $HOME/mcpl_src

# Install the OpenMC python API
pip install .
cd ../
