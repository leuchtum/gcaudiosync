import numpy as np
import copy
from gcaudiosync.gcanalyser.cncparameter import CNC_Parameter

class CNC_Status:

    active_movement = 0
    active_tool = 0

    position_linear = np.array([0.0, 0.0, 0.0])
    position_rotation = np.array([0.0, 0.0, 0.0])
    info_arc = np.array([2, 0.0, 0.0, 0.0, 0.0, 0])        # [direction, I, J, K, R, #turns]

    active_plane = 17

    absolute_position = True
    absolute_arc_center = False

    cutter_compensation = 40

    F_value = 0.0
    S_value = 0.0

    feed_rate = 0.0             # [mm/ms]
    spindle_speed = 0.0
    spindle_direction = "CW"
    spindle_on = False

    cooling_on = False

    exact_stop = False
    G_61_active = False

    program_end_reached = False

    # Constructor
    def __init__(self, 
                 start_position = False, 
                 CNC_Parameter: CNC_Parameter = None):

        if start_position:
            self.position_linear = np.copy(CNC_Parameter.START_POSITION_LINEAR)
            self.position_rotation = np.copy(CNC_Parameter.START_POSITION_ROTATION)

# Functions related to CNC_Status
# return a copy  of a CNC_Status
def copy_CNC_Status(Source: CNC_Status):

    new_CNC_Status = copy.deepcopy(Source)

    new_CNC_Status.exact_stop = new_CNC_Status.G_61_active

    return new_CNC_Status