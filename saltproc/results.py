import tables as tb
import numpy as np
import pandas as pd
import uncertainties.unumpy as unp

class Results():
    """Interface class for reading SaltProc results.

    Parameters
    ----------
    path : str
        Path of results file
    load_in_out_streams : bool
        Switch on whether or not to load waste streams.

    Attributes
    ----------

    time_at_eds : numpy.ndarray
        Cumulative time at each depletion step
    time_total : numpy.ndarray
        Cumulative time at each depletion step
        and each processing step.
    keff : numpy.ndarray
        :math:`k_\text{eff}` at each depletion and ...
    fisson_mass : numpy.ndarray
        Mass of fissionable nuclides summed over all
        depletable materials.
    breeding_ratio : numpy.ndarray
        Breeding ratio in the ...
    power_level : numpy.ndarray
        Power in [W].
    beta_eff : numpy.ndarray
        Timeseries of delayed neutron fractions.
    lambda_eff : numpy.ndarray
        Timesereis of delayed neutron precursor decay constants.
    depcode_metadata : dict of str to object
        Depletion code metadata, such as depletion code name, version, etc.
    depletion_step_metadata : dict of str to object
        Depletion step metadata, such as step runtime, memory usage, etc.
    nuclide_idx : dict of str to int
        A dictionary mapping nuclide name as a string to index.
    material_composition : dict of str to numpy.ndarray
       A dictionary mapping material name as a string to nuclide composition
       over time.
    material_parameters : dict of str to object
        A dictionary mapping material name as a string to material parameters
        (density, volume, burnup, etc.)
    waste_streams : dict of str to dict
        A dictionary mapping material name as a string to a dictionary mapping
        waste stream names as a string to the waste streams mass [g] as a
        timeseries.

    """
    def __init__(self, path, load_in_out_streams=True):
        f = tb.open_file(path, mode='r')
        root = f.root
        sim_params = root.simulation_parameters
        self.time_at_eds = sim_params.col('cumulative_time_at_eds')
        time_total = [[t1, t2] for (t1, t2) in zip (self.time_at_eds,
                                                    self.time_at_eds)]
        time_total = np.array(time_total).flatten()
        self.time_total = np.append(np.array([0]), time_total)

        self.keff = self._collect_eds_bds_params(sim_params, 'keff', errors=True)
        self.fission_mass = self._collect_eds_bds_params(sim_params, 'fission_mass')
        self.breeding_ratio = self._collect_eds_bds_params(sim_params, 'breeding_ratio', errors=True)
        self.power_level = sim_params.col('power_level')
        self.beta_eff = self._collect_eds_bds_params(sim_params, 'beta_eff', errors=True, multidim=True)
        self.lambda_eff = self._collect_eds_bds_params(sim_params, 'delayed_neutrons_lambda', errors=True, multidim=True)

        # metadata
        self.depcode_metadata = self._collect_metadata(f, 'depcode_metadata')
        self.depletion_step_metadata = self._collect_metadata(f, 'depletion_step_metadata', array=True)

        # Materials
        materials = root.materials
        nuclide_idx, material_composition, material_parameters, waste_streams = self._collect_material_params(materials, load_in_out_streams)
        self.nuclide_idx = nuclide_idx
        self.material_composition = material_composition
        self.material_parameters = material_parameters
        self.waste_streams = waste_streams

    def _collect_eds_bds_params(self, sim_params, col, errors=False, multidim=False):
        col_eds = sim_params.col(f'{col}_eds').tolist()
        col_bds = sim_params.col(f'{col}_bds').tolist()
        col = [col_bds[0], col_eds[0]]
        for (k1, k2) in zip(col_bds[1:], col_eds[1:]):
            col += [k1]
            col += [k2]
        col = np.array(col)
        if errors:
            if multidim:
                new_col = []
                for c in col:
                    c = np.array(c)
                    new_col += [unp.uarray(c[:,0], c[:,1]).tolist()]
                col = np.array(new_col)
            else:
                col = unp.uarray(col[:,0], col[:,1])
        return col

    def _collect_metadata(self, f, nodename, array=False):
        metadata = f.root[nodename]
        metadata = pd.DataFrame.from_records(metadata[:]).to_dict()
        for key, value in metadata.items():
            if array:
                metadata[key] = list(value.values())
            else:
                metadata[key] = value[0]
        return metadata

    def _collect_material_params(self, materials, load_in_out_streams):
        nuclide_idx = {}
        material_composition = {}
        material_parameters = {}
        waste_streams = {}
        for mat_name in materials._v_groups.keys():
            material = materials[mat_name]

            # main material composition
            nuclide_idx[mat_name], material_composition[mat_name] = self._collect_material_comp(material)

            # material parameters
            material_parameters[mat_name] = {}
            for property_name in material.before_reproc.parameters.colnames:
                material_parameters[mat_name][property_name] = \
                    self._collect_material_properties(material, property_name)

            # in and out streams
            waste_streams[mat_name] = {}
            if load_in_out_streams:
                for stream_name in material.in_out_streams._v_groups.keys():
                    waste_stream = material.in_out_streams[stream_name]
                    if len(waste_stream._v_children) > 0:
                        waste_streams[mat_name][stream_name] = \
                            self._collect_waste_streams(waste_stream, stream_name)

        return nuclide_idx, material_composition, material_parameters, waste_streams

    # MAKE THIS COLLECT IT INTO A TABLE/2D ARRAY
    def _collect_material_comp(self, material):
        nuc_map = material.before_reproc.nuclide_map
        nucs = list(map(bytes.decode, nuc_map.col('nuclide')))
        nuc_map = dict(zip(nucs, nuc_map.col('index')))
        arr_dim = (len(nuc_map), len(material.before_reproc.comp) + \
                   len(material.after_reproc.comp))
        material_comp = np.empty(arr_dim)
        for nuc in nucs:
            nuc_comp_br = material.before_reproc.comp[:, nuc_map[nuc]]
            nuc_comp_ar = material.after_reproc.comp[:, nuc_map[nuc]]
            nuc_comp_0 = nuc_comp_br.pop(0)
            nuc_comp = []
            for c1, c2 in zip(nuc_comp_br, nuc_comp_ar):
                nuc_comp = nuc_comp + [c1, c2]
            nuc_comp = [nuc_comp_0] + nuc_comp
            material_comp[nuc_map[nuc], :] = nuc_comp
        return nuc_map, material_comp

    def _collect_material_properties(self, material, col):
        col_br = material.before_reproc.parameters.col(col).tolist()
        col_ar = material.after_reproc.parameters.col(col).tolist()
        col_0 = col_br.pop(0)
        col_values = []
        for c1, c2 in zip(col_br, col_ar):
            col_values = col_values + [c1, c2]
        col_values = [col_0] + col_values
        return col_values


    def _collect_waste_streams(self, waste_stream, stream_name):
        nuc_map = waste_stream.nuclide_map
        nucs = list(map(bytes.decode, nuc_map.col('nuclide')))
        nuc_map = dict(zip(nucs, nuc_map.col('index')))
        waste_stream_comp = {}
        for nuc in nucs:
            nuc_comp = waste_stream.comp[:, nuc_map[nuc]]
            waste_stream_comp[nuc] = nuc_comp
        return waste_stream_comp

    # methods to get timeseries of various values
    def get_nuclide_mass(self, material, nuclide, timestep=None):
        """Get nuclide mass as a timeseries. If :attr:`timestep` is `None`,
        then return the mass at all times.

        Parameters
        ----------
        material : str
            Material name
        nuclide : str
            Nuclide string (e.g. 'U235')
        timestep : idx
            Timestep index

        Returns
        -------
        nuclide_mass : numpy.ndarray

        """
        nucmap = self.nuclide_idx[material]
        comp = self.material_composition[material]
        nuclide_mass = comp[nucmap[nuclide]]
        if timestep is not None:
            nuclide_mass = nuclide_mass[timestep]
        return nuclide_mass
