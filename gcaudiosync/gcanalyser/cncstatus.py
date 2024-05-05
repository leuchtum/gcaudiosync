import numpy as np
import copy

from gcaudiosync.gcanalyser.cncparameter import CNC_Parameter

class CNC_Status:

    active_movement: int    = 0     # active movement: 0: rapid linear, 1: linear, 2: arc CW, 3: arc CCW
    active_tool: int        = 0     # number of the active tool

    position_linear_axes = np.array([0.0, 0.0, 0.0])        # absolute positions for X, Y, Z in mm
    position_rotation_axes = np.array([0.0, 0.0, 0.0])      # absolute positions for A, B, C in mm
    info_arc = np.array([2, 0.0, 0.0, 0.0, 0.0, 0])         # all infos for an arc: 
                                                            # [direction, I, J, K, R, #turns]
                                                            # direction: 2 -> CW, 3 -> CCW
                                                            # I, J, K: absolute arc center in mm
                                                            # R: radius in mm
                                                            # #turns: number of turns

    active_plane: int           = 17        # active plane: XY -> 17, XZ -> 18, YZ -> 19

    absolute_position: bool     = True      # absolute position for X, Y, Z, A, B, C: True or false
    absolute_arc_center: bool   = False     # absolute position for I, J, K: True or False

    cutter_compensation = 40

    F_value: float = 0.0                # F value in m/min
    S_value: float = 0.0                # S value in RPM

    feed_rate: float        = 0.0       # feed rate in mm/ms
    spindle_speed: float    = 0.0       # spindle speed in RPM
    spindle_direction: str  = "CW"      # spindle direction: "CW" or "CCW"
    spindle_on: bool        = False     # spindle on: True or False

    cooling_on: bool        = False     # cooling on: True or False

    exact_stop: bool        = False     # exact stop: True or false
    G_61_active: bool       = False     # G61 active: True or false

    program_end_reached: bool   = False     # program end reached: True or False

    # Constructor
    def __init__(self, 
                 start_position = False, 
                 CNC_Parameter: CNC_Parameter = None):

        # change position if this is the first cnc-status for a g-code
        if start_position:
            self.position_linear_axes = np.copy(CNC_Parameter.START_POSITION_LINEAR_AXES)
            self.position_rotation_axes = np.copy(CNC_Parameter.START_POSITION_ROTATION_AXES)

    # end of class CNC_Status
###################################################################################################
# Functions related to CNC_Status

# return a copy  of a CNC_Status with all the important information copied for the next line in the g-code
def copy_CNC_Status(Source: CNC_Status):

    new_CNC_Status = copy.deepcopy(Source)

    new_CNC_Status.exact_stop = new_CNC_Status.G_61_active
    new_CNC_Status.info_arc[5] = 0

    return new_CNC_Status