LN="https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_31/JEFF312/ACE/"
SLUG="ACEs_"
EXT="K.zip"
SLUG1="STL_ACEs.zip"
ALL=(500 600 800 900 1000 1200 1500)
TEST=(900)

TEMPS=$TEST

#Uncomment if you want all temperatures (will take a long time)
#TEMPS=$ALL

for T in ${TEMPS[@]}
do
    wget $LN$SLUG$T$EXT
done

# Get thermal XS
wget -O ACEs_THERMK.zip $LN$SLUG1
