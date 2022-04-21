#!/bin/bash
set -ex

# Move cached OpenMC libaries to PATH
sudo mv $HOME/openmc_src/bin/openmc /usr/local/bin/openmc
sudo mv $HOME/openmc_src/lib/x86_64-linux-gnu /usr/local/lib/x86_64-linux-gnu/
sudo mv $HOME/openmc_src/share/openmc /usr/local/share/openmc
sudo mv $HOME/openmc_src/share/man /usr/local/share/man
sudo mv $HOME/openmc_src/include/openmc /usr/local/include/openmc
sudo mv $HOME/openmc_src/include/pugiconfig.hpp /usr/local/include/pugiconfig.hpp
sudo mv $HOME/openmc_src/include/pugixml.hpp /usr/local/include/pugixml.hpp
sudo mv $HOME/openmc_src/include/fmt /usr/local/include/fmt
sudo mv $HOME/openmc_src/include/xtl /usr/local/include/xtl
sudo mv $HOME/openmc_src/include/xtensor /usr/local/include/xtensor
sudo mv $HOME/openmc_src/include/gsl /usr/local/include/gsl
sudo mv $HOME/openmc_src/include/gsl-lite /usr/local/include/gsl-lite

