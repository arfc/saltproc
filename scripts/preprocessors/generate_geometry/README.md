## Instructions
SaltProc can now use OpenMC. We have written this conversion script for
easy conversion of your existing serpent geometry models to
the OpenMC format.

### Requirements:
- `openmc` version 0.13

You'll also need an openmc `material` that you have converted from your
serpent model. You can use the included `convert_material_serpent_to_openmc.py` script. We also encourage checking out more sophisticated tools like [`csg2csg`](https://github.com/makeclean/csg2csg) and [`neutronics_material_maker`](https://github.com/fusion-energy/neutronics_material_maker)

### Instructions:
From the command line, run:
```
python convert_geometry_serpent_to_openmc.py PATH_TO_GEO_FILE PATH_TO_MAT_FILE
```

### Note:
The following cards are unsupported, but we're working on adding support soon!
- `surf`
  - `inf` surface type (general use)
  - Truncated cylinders
  - `tri` (triangular prism)
  - `hexxprism`, `hexyprism`
  - `dode`
  - `ppd`
  - `cross` and `gcross`
  - `hexxap`,`hexyap`
  - `involute`
  - rounded corners on `sqc`
  - MCNP equivalent surface
  - User defined surface
- `lat`
  - hexagonal lattices
  - circular cluster array
  - vertical stack*
- `trans`
  - `rot` rotations
  - lattice transformations
- `usym`
- `pin`
