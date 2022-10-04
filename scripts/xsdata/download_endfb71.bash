#! ~/bin/bash

# Get conda working in non interactive shell
CONDA_PATH=$(conda info | grep -i 'base environment' | awk '{print $4}')
source $CONDA_PATH/etc/profile.d/conda.sh

################
### DOWNLOAD ###
################
# DATADIR is the directory where the xs library is extracted to
# @yardasol reccomends naming the parent directory where the files
# will be extractd to as "jeff312"
if [[ -d "$XSDIR" ]]
then
    DATADIR=$XSDIR/endfb71_ace
else
    DATADIR=$PWD/endfb71_ace
fi
mkdir -p $DATADIR/acedata

# ndy, decay, sfy data
LN="https://www.nndc.bnl.gov/endf-b7.1/zips/"
SLUG="ENDF-B-VII.1-"
DATA=("nfy" "decay" "sfy")
EXT=".zip"
for D in ${DATA[@]}
do
    if [[ ! -f $DATADIR/$SLUG$D$EXT ]]
    then
        wget -P $DATADIR $LN$SLUG$D$EXT
    fi
    mkdir -p $DATADIR/$D
    unzip -j $DATADIR/$SLUG$D$EXT -d $DATADIR/$D
    touch $DATADIR/endfb71.$D
    files=$(ls $DATADIR/$D/*.[Ee][Nn][Dd][Ff])
    for file in $files
    do
        cat $file >> $DATADIR/endfb71.$D
    done
done

# OpenMC depletion chain
#conda activate openmc-env
#python openmc_make_chain.py -D $DATADIR

#########################
### SETUP .xsdir FILE ###
#########################
XSDIR_FILE=endfb71.xsdir
ACESLUG=https://www.nndc.bnl.gov/endf-b7.1/aceFiles/
ACEGZ=ENDF-B-VII.1-tsl.tar.gz
if [[ ! -f $DATADIR/$ACEGZ ]]
then
    wget -P $DATADIR $ACESLUG$ACEGZ
fi
tar -xOzf $DATADIR/$ACEGZ xsdir | cat > $DATADIR/$XSDIR_FILE

# Make regex for DATADIR
DATADIR_REGEX=${DATADIR//\//\\\/}

# Fix datapath
sed -i "s/datapath/datapath=$DATADIR_REGEX\/acedata/" $DATADIR/$XSDIR_FILE
#echo "datapath=$DATADIR/acedata" > $DATADIR/$XSDIR_FILE

# Get cutoff line number
echo "Get cutoff"
LN="$(grep -n "directory" $DATADIR/$XSDIR_FILE)"
IFS=':' read -ra arr <<< "$LN"
LN=${arr[0]}

# Remove unused directory paths
head -n$LN $DATADIR/$XSDIR_FILE | cat > $DATADIR/temp
cat $DATADIR/temp > $DATADIR/$XSDIR_FILE
rm $DATADIR/temp
#echo "directory" >> $DATADIR/$XSDIR_FILE

# Neutron and thermal scattering data
LN="https://nucleardata.lanl.gov/lib/"
DATA=("endf71x" "ENDF71SaB")
EXT=".tgz"
for D in ${DATA[@]}
do
    if [[ ! -f $DATADIR/$D$EXT ]]
    then
        wget -P $DATADIR $LN$D$EXT
    fi
    tar -xzf $DATADIR/"$D$EXT" -C $DATADIR --verbose
    mv $DATADIR/$D/$D $DATADIR/acedata/.

    cat $DATADIR/$D/xsdir >> $DATADIR/$XSDIR_FILE
done


# download cross section dir convert script
if [[ ! -f $XSDIR/xsdirconvert.pl ]]
then
    wget -O $XSDIR/xsdirconvert.pl http://montecarlo.vtt.fi/download/xsdirconvert.pl
fi

# Run the xsdirconvert script
perl $XSDIR/xsdirconvert.pl $DATADIR/$XSDIR_FILE > $DATADIR/endfb71.xsdata
