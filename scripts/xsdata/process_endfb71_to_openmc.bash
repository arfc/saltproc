# Get conda working in non interactive shell
CONDA_PATH=$(conda info | grep -i 'base environment' | awk '{print $4}')
source $CONDA_PATH/etc/profile.d/conda.sh

if [[ -d "$XSDIR" ]]
then
    DATADIR=$XSDIR/endfb71_h5
else
    DATADIR=$PWD/endfb71_h5
fi
mkdir -p $DATADIR

conda activate $OPENMC_ENV

# Depletion cchain_endfb71_ace.xmlhain
python create_chain_from_endfb71.py -D $XSDIR/endfb71_ace
python $OPENMCDIR/scripts/openmc-ace-to-hdf5 -d $DATADIR --xsdir $XSDIR/endfb71_ace/endfb71.xsdir -m mcnp
mv chain_endfb71_ace.xml $DATADIR/chain_endfb71_ace.xml
