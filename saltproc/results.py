import tables as tb
import numpy as np
import pandas as pd
import uncertainties.unumpy as unp

class Results():
    """Interface class for reading SaltProc results"""

    def __init__(self, path):
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
        self.power_level = sim_params.col('power_level')
        self.breeding_ratio = sim_params.col('breeding_ratio')

        # metadata
        metadata = f.root.initial_depcode_siminfo
        metadata = pd.DataFrame.from_records(metadata[:]).to_dict()
        for key, value in metadata.items():
            metadata[key] = value[0]
        self.metadata = metadata

        # Materials
        materials = root.materials
        nuclide_idx, material_compositions, material_parameters, waste_streams = self._collect_material_params(materials)
        self.nuclide_idx = nuclide_idx
        self.material_compositions = material_compositions
        self.material_parameters = material_parameters
        self.waste_streams = waste_streams

    def _collect_eds_bds_params(self, sim_params, col, errors=False):
        col_eds = sim_params.col(f'{col}_eds').tolist()
        col_bds = sim_params.col(f'{col}_bds').tolist()
        col = [col_bds[0], col_eds[0]]
        for (k1, k2) in zip(col_bds[1:], col_eds[1:]):
            col = col + [k1]
            col = col + [k2]
        col = np.array(col)
        if errors == True:
            col = unp.uarray(col[:,0], col[:,1])
        return col

    def _collect_material_params(self, materials):
        nuclide_idx = {}
        material_compositions = {}
        material_parameters = {}
        waste_streams = {}
        for mat_name in materials._v_groups.keys():
            material = materials[mat_name]

            # main material composition
            nuclide_idx[mat_name], material_compositions[mat_name] = self._collect_material_comp(material)

            # material parameters
            material_parameters[mat_name] = {}
            for property_name in material.before_reproc.parameters.colnames:
                material_parameters[mat_name][property_name] = \
                    self._collect_material_properties(material, property_name)

            # in and out streams
            waste_streams[mat_name] = {}
            for stream_name in material.in_out_streams._v_groups.keys():
                waste_stream = material.in_out_streams[stream_name]
                if len(waste_stream._v_children) > 0:
                    waste_streams[mat_name][stream_name] = \
                        self._collect_waste_streams(waste_stream, stream_name)

        return nuclide_idx, material_compositions, material_parameters, waste_streams

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
