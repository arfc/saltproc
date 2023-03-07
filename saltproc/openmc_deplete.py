import argparse
import json

import openmc
import openmc.deplete as od


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
    dirctory : str
        Directory to write the XML files to.
    depletion_settings : str
        Path to the OpenMCDepcode depletion_settings file

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--materials',
                        type=str,
                        default=1,
                        help='path to openmc material material xml file')
    parser.add_argument('--geometry',
                        type=str,
                        default=1,
                        help='path to openmc geometry xml file')
    parser.add_argument('--settings',
                        type=str,
                        default=None,
                        help='path to openmc settings xml file')
    parser.add_argument('--tallies',
                        type=str,
                        default=None,
                        help='path to openmc tallies xml file')
    parser.add_argument('--directory',
                        type=str,
                        default=None,
                        help='path to output directory')
    args = parser.parse_args()
    return args


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

with open(f'{args.directory}/depletion_settings.json') as f:
    depletion_settings = json.load(f)

timesteps = depletion_settings.pop('timesteps')
fission_q = depletion_settings['operator_kwargs']['fission_q']
if not(fission_q is None):
    with open(fission_q, 'r') as f:
        fission_q = json.load(f)

    depletion_settings['operator_kwargs']['fission_q'] = fission_q

integrator_kwargs = depletion_settings.pop('integrator_kwargs')
model.deplete(timesteps, **depletion_settings, **integrator_kwargs)

del materials, geometry, settings, tallies, model
