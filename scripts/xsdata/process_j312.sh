################
### DOWNLOAD ###
################
#DATADIR is the directory where the xs library is extracted to
DATADIR=$(pwd)
LN="https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_31/JEFF312/ACE/"
SLUG="ACEs_"
EXT="K.zip"
SLUG1="STL_ACEs.zip"
TEMPS=(900)

#Uncomment for a good range of temperatures (will take a long time)
#TEMPS=(500 600 800 900 1000 1200 1500)

#Uncomment if you want all temperatures (will take a VERY long time)
#TEMPS=(300 400 500 600 700 800 900 1000 1200 1500 1800)

for T in ${TEMPS[@]}
do
    wget -P $DATADIR $LN$SLUG$T$EXT
done

# Get thermal XS
wget -O $DATADIR/ACEs_THERMK.zip $LN$SLUG1

# Get neutron induces and spontaneous fission yield data from JEFF 3.3
wget -O $DATADIR/sss_jeff33.nfy https://www.oecd-nea.org/dbdata/jeff/jeff33/downloads/JEFF33-nfy.asc
wget -O $DATADIR/sss_jeff33.sfy https://www.oecd-nea.org/dbdata/jeff/jeff33/downloads/JEFF33-sfy.asc

###############
### PROCESS ###
###############
DIRFILE=$DATADIR/sss_jeff312.xsdir
echo "datapath=$DATADIR/jeff312/acedata" | cat - > $DIRFILE 
echo "atomic weight ratios" | cat - >> $DIRFILE
mkdir -p $DATADIR/acedata

TEMPS=(900 "THERM")
#Uncomment if you have dowloaded the entire JEFF 3.1.2 libary
#TEMPS=(500 600 800 900 1000 1200 1500 "THERM")

# Regular expressions for changing the ZAI of 
# metastable isotopes
REGEXMETA=[A-Z][a-z]{0,1}[0-9]{1,3}M
REGEXZAI=[0-9]{1,3}[0-9]{3}\.[0-9]{2}c

# Regular expression for getting the atomic mass
REGEXAWT=[0-9]+\.[0-9]{6}

EXT="K.zip"
for T in ${TEMPS[@]}
do
    #Create directories for each temp and extract
    mkdir -p $DATADIR/$T
    unzip -j $DATADIR/ACEs_$T$EXT -d $DATADIR/$T
    
    # Change filenames to include temperature so we can put them all in the same
    # directory
    if [[ $T == "THERM" ]]
    then
        ACE=".ace"
        SUF=".ACE"
    else
        ACE=".ACE"
        SUF="-$T.ACE"
    fi
    files=$(ls $DATADIR/$T/*.[Aa][Cc][Ee])
    for file in $files
    do
        IFS='.' read -ra arr <<< "$file"
        PRE=${arr[0]}

        # Process isomeric states
        if [[ $PRE =~ $REGEXMETA ]]
        then
            echo ${arr[0]}
            LN="$(head -n 1 $file)"
            [[ $LN =~ $REGEXZAI ]]
            ZAI="${BASH_REMATCH[0]}"
            len=${#ZAI}
            index=$len-6
            ZAM="${ZAI:0:$index-1}3${ZAI:$index}"
            sed -i "s/$ZAI/$ZAM/" $file
            sed -i "s/$ZAI/$ZAM/" $PRE.dir
        fi
        sed -i "s/$ACE/$SUF/" $PRE.dir

        # Convert DOS to UNIX
        awk '{sub("\r$", ""); print }' $file > temp.ACE
        mv temp.ACE > $file

        # Get atomic weights
        if [[ $T == 900 ]]
        then
            LN="$(head -n 1 $PRE.dir)"
            [[ $LN =~ $REGEXZAI ]]
            ZAI="${BASH_REMATCH[0]}"
            [[ $LN =~ $REGEXAWT ]]
            AWT="${BASH_REMATCH[0]}"
            len=${#ZAI}
            ZAI="${ZAI:0:$len-4}"
            echo " $ZAI $AWT" | cat - >> $DIRFILE
        fi
    
        mv "$file" ${arr[0]}$SUF
    done
        
    mv $DATADIR/$T/*.ACE $DATADIR/acedata/.

    echo "directory" | cat - >> $DIRFILE
    # Add dir files to global dir file
    cat $DATADIR/$T/*.dir >> $DIRFILE 
    
    # Cleanup
    rm $DATADIR/$T/*.dir
done
