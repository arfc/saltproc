input_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/arfc/saltproc",
    "title": "SaltProc input file schema",
    "type": "object",
    "properties": {
        "proc_input_file": {
            "description": "File containing processing system objects",
            "type": "string"
        },
        "dot_input_file": {
            "description": "Graph file containing processing system structure",
            "type": "string"
        },
        "output_path": {
            "description": "Path output data storing folder",
            "type": "string",
            "pattern": "^\\.\\/(.*)$"
        },
        "depsteps": {
            "description": "Number of steps for constant power and depletion interval case",
            "type": "number"
        },
        "depcode": {
            "description": "Depcode class input parameters",
            "type": "object",
            "properties": {
                "codename": {
                    "description": "Name of depletion code",
                    "type": "string" },
                "exec_path": {
                    "description": "Path to depletion code executable",
                    "type": "string" },
                "template_inputfile_path": {
                    "description": "Path to user's template depletion code input file with reactor model",
                    "type": "string",
                    "pattern": "^\\.\\/(.*)$"},
                "iter_inputfile": {
                    "description": "Name of depletion code input file for depletion code rerunning",
                    "type": "string" },
                "iter_matfile": {
                    "description": "Name of iteratvie, rewritable material file for depletion code rerunning",
                    "type": "string" },
                "npop": {
                    "description": "Number of neutrons per generation",
                    "type": "number",
                    "minimum": 0},
                "active_cycles": {
                    "description": "number of active generations",
                    "type": "number",
                    "minimum": 0},
                "inactive_cycles": {
                    "description": "Number of inactive generations",
                    "type": "number",
                    "minimum": 0},
                "geo_file_paths": {
                    "description": "Path(s) to geometry file(s) to swtich to in depletion code runs",
                    "type": "array",
                    "items": { "type": "string"},
                    "minItems": 1,
                    "uniqueItems": False
                }
            },
            "required": ["codename", "exec_path", "template_inputfile_path", "iter_inputfile", "iter_matfile", "npop", "active_cycles","inactive_cycles", "geo_file_paths"]
        },
       "simulation": {
           "description": "Simulation class input parameters",
           "type": "object",
           "properties": {
               "sim_name": {
                   "description": "Name of simulation",
                   "type": "string"},
               "db_name": {
                   "description": "Output HDF5 database file name",
                   "type": "string",
                    "pattern": "^(.*)\\.h5$"},
               "restart_flag": {
                   "description": "Restart simulation from the step when it stopped?",
                   "type": "boolean"},
               "adjust_geo": {
                   "description": "switch to another geometry when keff drops below 1?",
                   "type": "boolean"}
           },
           "requires": ["sim_name", "db_name", "restart_flag", "adjust_geo"]
       },
       "reactor": {
           "description": "Reactor class input parameters",
           "type": "object",
           "properties": {
               "volume": {
                   "description": "reactor core volume [cm^3]",
                   "type": "number",
                    "minimum": 0},
               "mass_flowrate": {
                   "description": "Salt mass flowrate through reactor core [g/s]",
                   "type": "number",
                    "minimum": 0 },
               "power_levels": {
                   "description": "Reactor power or power step list durng depletion step [W]",
                   "type": "array",
                   "items": { "type": "number",
                    "minimum": 0},
                   "minItems": 1,
                   "uniqueItems": False
                },
               "depl_hist": {
                   "description": "Depletion step interval or cumulative time (end of step) [d]",
                   "type": "array",
                   "items": { "type": "number",
                    "minimum": 0},
                   "minItems": 1,
                   "uniqueItems": False
                }
           },
           "required": ["volume", "mass_flowrate", "power_levels", "depl_hist"]
       }
    },
    "required": ["proc_input_file", "dot_input_file", "output_path", "depsteps", "depcode", "simulation", "reactor"]
}