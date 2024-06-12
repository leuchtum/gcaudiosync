import numpy as np
import math

import gcaudiosync.gcanalyser.vectorfunctions as vecfunc
import gcaudiosync.gcanalyser.numericalmethods as nummet

from gcaudiosync.gcanalyser.movement import *

def function(x):
    return x**2 - 0

v0 = [0, 0]
v_target = 7
max_acc = [0.6, 0.6]
period_time = 1.5
phase = 0
direction = 3


time = compute_start_time_arc_movement(v0,
                                        v_target,
                                        max_acc,
                                        period_time,
                                        phase,
                                        direction)

print(time)