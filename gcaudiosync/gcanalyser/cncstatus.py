import numpy as np
import copy

from gcaudiosync.gcanalyser.cncparameter import CNCParameter
from gcaudiosync.gcanalyser.linearaxes import LinearAxes
from gcaudiosync.gcanalyser.rotationaxes import RotationAxes
from gcaudiosync.gcanalyser.arcinformation import ArcInformation

class CNCStatus:
    """
    Represents the status of a CNC machine.

    This class stores the current state of various parameters during CNC machining operations.

    Attributes:
        active_movement_type (int): Active movement type: 0 for rapid linear, 1 for linear, 2 for arc CW, 3 for arc CCW.
        active_tool (int): Number of the active tool.
        position_linear_axes (LinearAxes): Absolute positions for X, Y, Z in mm.
        position_rotation_axes (RotationAxes): Absolute positions for A, B, C in mm.
        arc_information (ArcInformation): Information about arcs.
        active_plane (int): Active plane: XY (17), XZ (18), YZ (19).
        absolute_position (bool): Flag for absolute position for X, Y, Z, A, B, C.
        absolute_arc_center (bool): Flag for absolute position for I, J, K.
        cutter_compensation (int): Cutter compensation.
        F_value (float): F value in m/min.
        S_value (float): S value in RPM.
        feed_rate (float): Feed rate in mm/ms.
        spindle_speed (float): Spindle speed in RPM.
        spindle_direction (str): Spindle direction: "CW" or "CCW".
        spindle_on (bool): Spindle on: True or False.
        cooling_on (bool): Cooling on: True or False.
        exact_stop (bool): Exact stop: True or False.
        G_61_active (bool): G61 active: True or False.
        program_end_reached (bool): Program end reached: True or False.
    """

    # Constructor
    def __init__(self, 
                 start_position = False, 
                 CNC_Parameter: CNCParameter = None):
        """
        Initializes the CNCStatus object.

        Args:
            start_position (bool): Whether to set the start position. Defaults to False.
            CNC_Parameter (CNCParameter): CNC parameters to initialize with. Defaults to None.
        """

        self.active_movement_type: int   = 0         # Active movement: 0: rapid linear, 1: linear, 2: arc CW, 3: arc CCW
        self.active_tool: int            = 0         # Number of the active tool

        self.position_linear_axes = LinearAxes()     # Absolute positions for X, Y, Z in mm
        self.position_rotation_axes = RotationAxes() # Absolute positions for A, B, C in mm
        self.arc_information = ArcInformation()      # All infos for an arc

        self.active_plane: int           = 17        # Active plane: XY -> 17, XZ -> 18, YZ -> 19

        self.absolute_position: bool     = True      # Absolute position for X, Y, Z, A, B, C: True or false
        self.absolute_arc_center: bool   = False     # Absolute position for I, J, K: True or False

        self.cutter_compensation = 40                # Cutter compensation

        self.F_value: float = 0.0                    # F value in m/min
        self.S_value: float = 0.0                    # S value in RPM

        self.feed_rate: float = 0.0                  # Feed rate in mm/ms

        self.spindle_speed: float    = 0.0           # Spindle speed in RPM
        self.spindle_direction: str  = "CW"          # Spindle direction: "CW" or "CCW"
        self.spindle_on: bool        = False         # Spindle on: True or False

        self.cooling_on: bool        = False         # Cooling on: True or False

        self.exact_stop: bool        = False         # Exact stop: True or false
        self.G_61_active: bool       = False         # G61 active: True or false

        self.program_end_reached: bool   = False     # Program end reached: True or False

        # Change position if this is the first cnc-status for a g-code
        if start_position:
            self.position_linear_axes = copy.deepcopy(CNC_Parameter.START_POSITION_LINEAR_AXES)
            self.position_rotation_axes = copy.deepcopy(CNC_Parameter.START_POSITION_ROTATION_AXES)

    #################################################################################################
    # Methods

    # end of class CNC_Status
###################################################################################################
# Functions related to CNC_Status

# return a copy  of a CNC_Status with all the important information copied for the next line in the g-code
def copy_CNC_Status(Source: CNCStatus) -> CNCStatus:
    """
    Returns a copy of a CNCStatus object.

    Args:
        Source (CNCStatus): The source CNCStatus object to copy.

    Returns:
        CNCStatus: A new CNCStatus object with all the important information copied for the next line in the G-code.
    """

    # Make new cnc status
    new_CNC_Status: CNCStatus = copy.deepcopy(Source)

    # Change all parameters that are only active in one line
    new_CNC_Status.exact_stop = new_CNC_Status.G_61_active

    return new_CNC_Status