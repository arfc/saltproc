import openmc
import openmc.deplete as od
import argparse


def parse_arguments():
    """Parses arguments from command line.

    Parameters
    ----------
    materials : str
        Path to openmc material `.xml` file
    geometry : int
        Path to openmc geometry `.xml` file
    settings : str
        Path to openmc settings `.xml` file
    tallies : str
        Path to openmc tallies `.xml` file
    depletion_settings : str
        Path to the OpenMCDepcode depletion_settings file

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--materials',
                        type=str,
                        default=1,
                        help='path to openmc material \
                        material xml file')
    parser.add_argument('--geometry',
                        type=str,
                        default=1,
                        help='path to openmc geometry \
                        xml file')
    parser.add_argument('--settings',
                        type=str,
                        default=None,
                        help='path to openmc settings \
                        xml file')
    parser.add_argument('--tallies',
                        type=str,
                        default=None,
                        help='path to openmc tallies \
                        xml file')
    parser.add_argument('--depletion_settings',
                        type=str,
                        default=None,
                        help='path to saltproc depletion \
                        settings  json file')
    args = parser.parse_args()
    return str(args.materials), str(args.geometry), str(args.settings), \
        str(args.tallies), str(args.depletion_settings)


args = parse_arguments()

# Initalize OpenMC objects
materials = openmc.Materials.from_xml(path=args.materials)
geometry = openmc.Geometry.from_xml(path=args.geometry, materials=materials)
settings = openmc.Settings.from_xml(args.settings)
tallies = openmc.Tallies.from_xml(args.tallies)
model = openmc.model.Model(materials=materials,
                           geometry=geometry,
                           settings=settings,
                           tallies=tallies)

with open(args.depletion_settings) as f:
    depletion_settings = json.load(f)

model.deplete(depletion_settings['timesteps'],
              directory=depletion_settings['directory'],
              operator_kwargs=depletion_settings['operator_kwargs'],
              **depletion_settings['integrator_kwargs'])

del materials, geometry, settings, tallies, model
