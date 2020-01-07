from saltproc import Depcode
serpent_dep_m_out = './tap.serpent'
new_mat_file = './saltproc_prepr_comp.ini'

depcode = Depcode(codename='SERPENT',
                  exec_path=None,
                  template_fname=None,
                  input_fname=serpent_dep_m_out,
                  output_fname=None,
                  iter_matfile=None,
                  geo_file=None)
mats = depcode.read_dep_comp(serpent_dep_m_out, 0)
depcode.write_mat_file(mats, new_mat_file, 0)
