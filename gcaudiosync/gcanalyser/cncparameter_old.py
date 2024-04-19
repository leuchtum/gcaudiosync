import numpy as np

class CNC_Parameter:
    
    # Machine parameter

    tool_change_point = np.array([100, 100, 100])

    F_max = 20000       # max feed rate in mm/min
    S_max = 18000       # max spindle speed in RPM

    max_a_X = 40        # max acceleration/deceleration of X-Axis in mm/s^2
    max_a_Y = 40        # max acceleration/deceleration of Y-Axis in mm/s^2
    max_a_Z = 40        # max acceleration/deceleration of Z-Axis in mm/s^2
    max_a_A = 0.5       # max acceleration/deceleration of A-Axis in rad/s^2
    max_a_B = 0.5       # max acceleration/deceleration of B-Axis in rad/s^2
    max_a_C = 0.5       # max acceleration/deceleration of C-Axis in rad/s^2

    tool_change_time = 8000     # [ms]

    commands = {
                "abort":                0,
                "quit":                 1,
                "progabort":            2,
                "spindle_start_CW":     3,
                "spindle_start_CCW":    4,
                "spindle_off":          5,
                "tool_change":          6,
                "cooling_on":           8,
                "cooling_off":          9,
                "end_of_program":      30,
                }

    def __init__(self):
        pass