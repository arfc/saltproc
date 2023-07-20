#! ~/bin/bash
set -ex
################
### DOWNLOAD ###
################
# Serpent version 2.32 added support for interpolating continuous energy thermal
# scattering cross sections. If a user has this serpent version, then the script
# will download the ENDF/B-VII.1 thermal scattering data which is continuous in
# energy. Otherwise, the script will download the ENDF/B-VII.0 thermal scattering
# data which is tabulated in energy, but is the same evaluation as the ENDF/B-VII.1 data
SUPPORTS_INTERPOLATE_CONTINUOUS_ENERGY=false
# DATADIR is the directory where the xs library is extracted to
# @yardasol reccomends naming the parent directory where the files
# will be extractd to as "endfb71_ace"
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
DATA=("nfy" "decay" "neutrons")
EXT=".zip"
for D in ${DATA[@]}
do
    if [[ ! -f $DATADIR/$SLUG$D$EXT ]]
    then
        wget -P $DATADIR $LN$SLUG$D$EXT
    fi
    if [[ ! -d $DATADIR/$D ]]
    then
        mkdir -p $DATADIR/$D
        unzip -j $DATADIR/$SLUG$D$EXT -d $DATADIR/$D
    fi
    # Remove Be7 evaluation
    if [[ -f $DATADIR/$D/dec-004_Be_007.endf ]]
    then
        rm $DATADIR/$D/dec-004_Be_007.endf
    fi
    if [[ -f $DATADIR/$D/n-004_Be_007.endf ]]
    then
        rm $DATADIR/$D/n-004_Be_007.endf
    fi
    if [[ $D -ne "neutrons" ]]
    then
        if [[ ! -f $DATADIR/endfb71.$D ]]
        then
            touch $DATADIR/endfb71.$D
            files=$(ls $DATADIR/$D/*.[Ee][Nn][Dd][Ff])
            for file in $files
            do
                cat $file >> $DATADIR/endfb71.$D
            done
        fi
    fi
done

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
sed -i "s/datapath /datapath=$DATADIR_REGEX/" $DATADIR/$XSDIR_FILE

# Get cutoff line number
LN="$(grep -n "directory" $DATADIR/$XSDIR_FILE)"
IFS=':' read -ra arr <<< "$LN"
LN=${arr[0]}

# Remove unused directory paths
head -n$LN $DATADIR/$XSDIR_FILE | cat > $DATADIR/temp
cat $DATADIR/temp > $DATADIR/$XSDIR_FILE
rm $DATADIR/temp

# Neutron and thermal scattering data
LN="https://nucleardata.lanl.gov/lib/"
if ! $SUPPORTS_INTERPOLATE_CONTINUOUS_ENERGY
then
    THERM="endf70sab"
else
    THERM="ENDF71SaB"
fi
DATA=("$THERM" "endf71x")
EXT=".tgz"
for D in ${DATA[@]}
do
    if [[ ! -f $DATADIR/$D$EXT ]]
    then
        wget -P $DATADIR $LN$D$EXT
    fi
    if [[ ! -d $DATADIR/acedata/$D ]]
    then
        tar -xzf $DATADIR/"$D$EXT" -C $DATADIR --verbose
        mv $DATADIR/$D/$D $DATADIR/acedata/.
    fi
    if [[ $D == "endf71x" ]]
    then
        # Remove old hydrogen evaluations
        rm -f $DATADIR/acedata/$D/H/H1001.71*
        sed -i "s/.*H\/1001\.71.*//" $DATADIR/$D/xsdir

        ## Remove bad Be7 evaluation
        #rm -f $DATADIR/acedata/$D/Be/4007*
        #sed -i "s/.*Be\/4007.*//" $DATADIR/$D/xsdir
    else
        if $SUPPORTS_INTERPOLATE_CONTINUOUS_ENERGY
        then
            if [[ -f $DATADIR/acedata/$D/sio2.10t ]]
            then
                rm -f $DATADIR/acedata/$D.sio2.2*
                rm -f $DATADIR/acedata/$D.sio2.3*
                sed -i "s/.*sio2\.2.*//" $DATADIR/$D/xsdir
                sed -i "s/.*sio2\.3.*//" $DATADIR/$D/xsdir
            fi
            if [[ -f $DATADIR/acedata/$D/u-o2.30t ]]
            then
                rm -f $DATADIR/acedata/$D.u-o2.2*
                sed -i "s/.*u-o2\.2.*//" $DATADIR/$D/xsdir
            fi
            if [[ -f $DATADIR/acedata/$D/zr-h.30t ]]
            then
                rm -f $DATADIR/acedata/$D.zr-h.2*
                sed -i "s/.*zr-h\.2.*//" $DATADIR/$D/xsdir
            fi
        fi
    fi

    cat $DATADIR/$D/xsdir >> $DATADIR/$XSDIR_FILE
    echo "" >> $DATADIR/$XSDIR_FILE
    sed -i "s/$D\//acedata\/$D\//" $DATADIR/$XSDIR_FILE
done


# download cross section dir convert script
if [[ ! -f $XSDIR/xsdirconvert.pl ]]
then
    wget -O $XSDIR/xsdirconvert.pl http://montecarlo.vtt.fi/download/xsdirconvert.pl
fi

# Run the xsdirconvert script
perl $XSDIR/xsdirconvert.pl $DATADIR/$XSDIR_FILE > $DATADIR/endfb71.xsdata

# Fix bad names for Am242
sed -i "s/Am-242/Am-242m/" $DATADIR/endfb71.xsdata
sed -i "s/ Am-242/Am-242/" $DATADIR/endfb71.xsdata
sed -i "s/Am-242mm/ Am-242/" $DATADIR/endfb71.xsdata
sed -i "s/c  1  95242  0/c  1  95242  2/" $DATADIR/endfb71.xsdata
sed -i "s/c  1  95242  1/c  1  95242  0/" $DATADIR/endfb71.xsdata
sed -i "s/c  1  95242  2/c  1  95242  1/" $DATADIR/endfb71.xsdata
sed -i "s/c  1  95042  0/c  1  95242  0/" $DATADIR/endfb71.xsdata
