## Instructions
SaltProc needs separate file with compositions of all burnable materials (see examples/mats/).
This file must be preprocessed to include all isotopes from the library in it, most of them will have zero mass fraction (it is neccesary to normal Serpent runs).

To preprocess file with material composition:
1) Run Serpent depletion for single depletion step. You may use example input file for Serpent: examples/tap.serpent.
2) Change path to Serpent output and desired name for preprocessed composition file in create_prepr_composition.py
2) Run Python-script to read Serpent output and generate file with material composition.

Number of burnable materials is not limited. Non-burnable materials must be kept it separate file.
