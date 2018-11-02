import os
from depcode import Depcode

input_path = os.path.dirname(os.path.abspath(__file__))
print(input_path)
input_file = os.path.join(input_path, 'data/saltproc_rebus.inp')
template_file = os.path.join(input_path, 'data/rebus.inp')
# executable path of Serpent
exec_path = '/home/andrei2/serpent/serpent2/src_2130/sss2'
# Number of cores and nodes to use in cluster
cores = 4

if __name__ == "__main__":
    print('Initiating Saltproc:\n'
          # '\tRestart = ' + str(restart) + '\n'
          # '\tNodes = ' + str(nodes) + '\n'
          '\tCores = ' + str(cores) + '\n'
          # '\tSteps = ' + str(steps) + '\n'
          # '\tBlue Waters = ' + str(bw) + '\n'
          '\tSerpent Path = ' + exec_path + '\n'
          '\tTemplate File Path = ' + template_file + '\n'
          '\tInput File Path = ' + input_file + '\n'
          # '\tMaterial File Path = ' + mat_file + '\n'
          # '\tOutput DB File Path = ' + db_file + '\n'
          )

    run = Depcode(codename='SERPENT',
                  exec_path=exec_path,
                  template_fname=template_file,
                  input_fname=input_file,
                  output_fname='NONE',
                  npop=444,
                  active_cycles=100,
                  inactive_cycles=20)
#    run.run_depcode(cores)
# print('End of RUN')
    # run.read_depcode_template()
    run.write_depcode_input(template_file, input_file)
