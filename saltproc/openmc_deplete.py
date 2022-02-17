import openmc
import openmc.deplete as od
import argparse

def parse_arguments():
    """Parses arguments from command line.

    Parameters
    ----------

    Returns
    -------
    materials: str
        Path to openmc material `.xml` file
    geometry: int
        Path to openmc geometry `.xml` file
    settings: str
        Path to openmc settings `.xml` file
    depletion_settings: str
        Path to the DepcodeOpenMC depletion_settings file

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-mat',      # Number of nodes to use
                        type=int,
                        default=1,
                        help='path to openmc material \
                        material xml file')
    parser.add_argument('-geo',      # Number of cores to use
                        type=int,
                        default=1,
                        help='path to openmc geometry \
                        xml file')
    parser.add_argument('-set',      # main input file
                        type=str,
                        default=None,
                        help='path to openmc settings \
                        xml file')
    args = parser.parse_args()
    return int(args.mat), int(args.geo), str(args.set)


# Initalize OpenMC objects
materials = openmc.Materials.from_xml(path=args.mat)
geometry = openmc.Geometry.from_xml(path=args.geo, materials=materials)
settings = openmc.Settings.from_xml(args.set)
tallies = openmc.Tallies.from_xml('./saltproc_tallies.xml')

## NEED TO IMPLEMENT FUNCTION TO MAKE THIS XML ##
## IN DepcodeOpenMC ##
depletion_settings = # read xml object from file?

model = openmc.model.Model(materials=materials,
                           geometry=geometry,
                           settings=settings
                           tallies=tallies)

model.deplete(depletion_settings['timesteps'],
              directory=depletion_settings['directory']
              operator_kwargs=depletion_settings['operator_kwargs'],
              depletion_settings['integrator_kwargs'])
