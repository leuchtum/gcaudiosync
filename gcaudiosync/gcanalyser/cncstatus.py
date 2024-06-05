import numpy as np
import copy

from gcaudiosync.gcanalyser.cncparameter import CNCParameter
from gcaudiosync.gcanalyser.linearaxes import LinearAxes
from gcaudiosync.gcanalyser.rotationaxes import RotationAxes
from gcaudiosync.gcanalyser.arcinformation import ArcInformation

class CNCStatus:

    active_movement_type: int   = 0         # active movement: 0: rapid linear, 1: linear, 2: arc CW, 3: arc CCW
    active_tool: int            = 0         # number of the active tool

    position_linear_axes = LinearAxes()     # absolute positions for X, Y, Z in mm
    position_rotation_axes = RotationAxes() # absolute positions for A, B, C in mm
    arc_information = ArcInformation()      # all infos for an arc

    active_plane: int           = 17        # active plane: XY -> 17, XZ -> 18, YZ -> 19

    absolute_position: bool     = True      # absolute position for X, Y, Z, A, B, C: True or false
    absolute_arc_center: bool   = False     # absolute position for I, J, K: True or False

    cutter_compensation = 40                # cutter compensation

    F_value: float = 0.0                    # F value in m/min
    S_value: float = 0.0                    # S value in RPM

    feed_rate: float        = 0.0           # feed rate in mm/ms
    spindle_speed: float    = 0.0           # spindle speed in RPM
    spindle_direction: str  = "CW"          # spindle direction: "CW" or "CCW"
    spindle_on: bool        = False         # spindle on: True or False

    cooling_on: bool        = False         # cooling on: True or False

    exact_stop: bool        = False         # exact stop: True or false
    G_61_active: bool       = False         # G61 active: True or false

    program_end_reached: bool   = False     # program end reached: True or False

    # Constructor
    def __init__(self, 
                 start_position = False, 
                 CNC_Parameter: CNCParameter = None):

        # change position if this is the first cnc-status for a g-code
        if start_position:
            self.position_linear_axes = copy.deepcopy(CNC_Parameter.START_POSITION_LINEAR_AXES)
            self.position_rotation_axes = copy.deepcopy(CNC_Parameter.START_POSITION_ROTATION_AXES)

    # end of class CNC_Status
###################################################################################################
# Functions related to CNC_Status

# return a copy  of a CNC_Status with all the important information copied for the next line in the g-code
def copy_CNC_Status(Source: CNCStatus):

    new_CNC_Status = copy.deepcopy(Source)

    new_CNC_Status.exact_stop = new_CNC_Status.G_61_active

    return new_CNC_Status