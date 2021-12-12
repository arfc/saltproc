#DATADIR is the directory where the xs library is extracted to
DATADIR=$(pwd)
LN="https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_31/JEFF312/ACE/"
SLUG="ACEs_"
EXT="K.zip"
SLUG1="STL_ACEs.zip"
TEMPS=(900)

#Uncomment if you want all temperatures (will take a long time)
#TEMPS=(500 600 800 900 1000 1200 1500)

for T in ${TEMPS[@]}
do
    wget -P $DATADIR $LN$SLUG$T$EXT
done

# Get thermal XS
wget -O $DATADIR/ACEs_THERMK.zip $LN$SLUG1
