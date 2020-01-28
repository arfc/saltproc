import numpy as np
import json
import os
import matplotlib.pyplot

# First period: operation on 100% power level, uniform timestep
# 96 hours with depstep=12hour
# Note: Do not include 0.0 time point
depstep1 = 12/24
start_time = 0.0 + depstep1
end_time = 96/24
power_level1 = 1.250E+9
nsteps1 = int(end_time/depstep1)

dep_hist1 = np.linspace(start_time, end_time, num=nsteps1)
pow_hist1 = power_level1*np.ones_like(dep_hist1)

print(dep_hist1, pow_hist1, nsteps1)

# Second period: decreasing power level to 0% with rampspeed 10%/min
# 10 minutes with time resolution 30sec
depstep2 = 0.5  # minutes
start_time2 = end_time*24*60 + depstep2
t2 = 10         # minutes
end_time2 = start_time2 + t2
power_level2 = 0.0
nsteps2 = int(t2/depstep2)
powstep2 = (power_level1-power_level2)/nsteps2
# Convert from minutes to days
dep_hist2 = (1/(24*60))*np.linspace(start_time2,
                                    end_time2, num=nsteps2, endpoint=False)
pow_hist2 = np.linspace(power_level1,
                        power_level2,
                        num=nsteps2,
                        endpoint=False)

print(dep_hist2, pow_hist2, nsteps2, powstep2)

# Third period: staying on 0% power level
# 7.66 hours too reach Xe135 peak
# 10 min resolution
depstep3 = 10  # minutes
start_time3 = end_time2 + depstep3
t3 = 460  # min, 7.66 hours
end_time3 = start_time3 + t3
nsteps3 = int(t3/depstep3)
dep_hist3 = (1/(24*60))*np.linspace(start_time3,
                                    end_time3,
                                    num=nsteps3,
                                    endpoint=False)
pow_hist3 = power_level2*np.ones_like(dep_hist3)

print(dep_hist3, pow_hist3, nsteps3)

# Fourth period: ramp up with 10%/min back to 100%
# 10 minutes with time resolution 30sec
depstep4 = 0.5  # minutes
start_time4 = end_time3 + depstep4
t4 = 10         # minutes
end_time4 = start_time4 + t4
power_level4 = power_level1
nsteps4 = int(t4/depstep4)
powstep4 = (power_level4-power_level2)/nsteps2
# Convert from minutes to days
dep_hist4 = (1/(24*60))*np.linspace(start_time4,
                                    end_time4,
                                    num=nsteps4,
                                    endpoint=False)
pow_hist4 = powstep4+np.linspace(power_level2,
                                 power_level4,
                                 num=nsteps4,
                                 endpoint=False)

print(dep_hist4, pow_hist4, nsteps4, powstep4)

# Fifth period, operation on 100% power level
# time resolution = 10 minutes, 10 hours
depstep5 = 10  # minutes
start_time5 = end_time4 + depstep5
t5 = 600  # min, 10 hours
end_time5 = start_time5 + t5
nsteps5 = int(t5/depstep5)
dep_hist5 = (1/(24*60))*np.linspace(start_time5,
                                    end_time5,
                                    num=nsteps5,
                                    endpoint=False)
pow_hist5 = power_level1*np.ones_like(dep_hist5)

print(dep_hist5, pow_hist5, nsteps5)

# Six period

# Cue everything together
dep_hist = [*dep_hist1, *dep_hist2, *dep_hist3, *dep_hist4, *dep_hist5]
pow_hist = [*pow_hist1, *pow_hist2, *pow_hist3, *pow_hist4, *pow_hist5]

print(len(dep_hist), len(pow_hist))

# Initialize figure
fig_1 = matplotlib.pyplot.figure(1)
ax = fig_1.add_subplot(111)
ax.grid(True)
ax.plot(dep_hist, pow_hist, '+-')

# ax.legend(loc=0)
ax.set_ylabel(r'Power level [W]')
ax.set_xlabel('EFPD')
ax.set_title(r'Power dynamics during load folowing')
fig_1.savefig('power.png')

json_dict = {}

json_dict["Depletion step interval or Cumulative time (end of step) (d)"] = \
            dep_hist
json_dict["Reactor power or power step list during depletion step (W)"] = \
            pow_hist
# Write list in json file file
path = os.path.dirname(os.path.abspath(__file__))
json_file = os.path.join(path, 'cumulative_time_and_power_inout.json')
with open(json_file, 'w') as f:
    json.dump(json_dict, f, ensure_ascii=False)
