#!/bin/bash
set -ex

# Move cached OpenMC libaries to PATH
sudo mv $HOME/openmc_src/bin/openmc /usr/local/bin/openmc
OPENMC_LIBS=(libopenmc.so cmake libpugixml.a pkgconfig)
for LIB in ${OPENMC_LIBS[@]}; do
    sudo mv $HOME/openmc_src/lib/$LIB /usr/local/lib/.
done

sudo mv $HOME/openmc_src/lib/ /usr/local/lib/
#sudo mv $HOME/openmc_src/share/openmc /usr/local/share/openmc
#sudo mv $HOME/openmc_src/share/man /usr/local/share/man
INCLUDES=(fmt xtl xtensor gsl gsl-lite openmc pugixml.hpp pugiconfig.hpp)
for I in ${INCLUDES[@]}; do
    sudo mv $HOME/openmc_src/include/$I /usr/local/include/$I
done

# Move MCPL stuff
MCPL_BINARIES=(pymcpltool mcpl-config mcpltool mcpl2ssw ssw2mcpl mcpl2phits phits2mcpl)
for BINARY in ${MCPL_BINARIES[@]}; do
    sudo mv $HOME/mcpl_src/bin/$BINARY /usr/local/bin/.
done

MCPL_LIBS=(libsswmcpl.so libphitsmcpl.so libmcpl.so)
for LIB in ${MCPL_LIBS[@]}; do
    sudo mv $HOME/mcpl_src/lib/$LIB /usr/local/lib/.
done
sudo mv $HOME/mcpl_src/include/mcpl.h /usr/local/include/.
sudo mv $HOME/mcpl_src/share/MCPL /usr/local/share/.
