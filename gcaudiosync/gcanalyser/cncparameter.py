import numpy as np

from gcaudiosync.gcanalyser.lineextractor import Line_Extractor
from gcaudiosync.gcanalyser.filefunctions import *

class CNC_Parameter:
    
    # Machine parameter
    START_POSITION_LINEAR_AXES          = np.array([100.0, 100.0, 100.0])
    START_POSITION_ROTATION_AXES        = np.array([0.0, 0.0, 0.0])
    TOOL_CHANGE_POSITION_LINEAR_AXES    = np.array([100.0, 100.0, 100.0])

    S_IS_ABSOLUTE: bool = True      # True if S value is absolute

    F_MAX: float = 20000.0          # max feed rate in mm/min
    S_MAX: float = 18000.0          # max spindle speed in RPM

    MAX_A_X: float = 40.0           # max acceleration/deceleration of X-Axis in mm/s^2
    MAX_A_Y: float = 40.0           # max acceleration/deceleration of Y-Axis in mm/s^2
    MAX_A_Z: float = 40.0           # max acceleration/deceleration of Z-Axis in mm/s^2

    TOOL_CHANGE_TIME: int = 8000    # [ms]

    # M commands
    COMMAND_ABORT: float                = 0.0
    COMMAND_QUIT : float                = 1.0
    COMMAND_PROGABORT                   = 2.0
    COMMAND_SPINDLE_START_CW            = 3.0
    COMMAND_SPINDLE_START_CCW: float    = 4.0
    COMMAND_SPINDLE_OFF: float          = 5.0
    COMMAND_TOOL_CHANGE: float          = 6.0
    COMMAND_COOLING_ON: float           = 8.0
    COMMAND_COOLING_OFF: float          = 9.0
    COMMAND_END_OF_PROGRAM: float       = 30.0

    # Constructor
    def __init__(self, 
                 parameter_src: str = ""):
        
        # Get the parameter from the parameter list
        parameter: str = read_file(parameter_src)    

        # Make an Extractor
        Extractor: Line_Extractor = Line_Extractor()

        # No src for cnc-parameter given
        if len(parameter) == 0:
            print("Using default CNC-parameter.")

        # Non number parameter
        non_number_parameter = ["S_IS_ABSOLUTE",
                                "START_POSITION_X",
                                "START_POSITION_Y",
                                "START_POSITION_Z",
                                "TOOL_CHANGE_POSITION_X",
                                "TOOL_CHANGE_POSITION_Y",
                                "TOOL_CHANGE_POSITION_Z",]

        # Go through cnc-parameter
        for line in parameter:

            information = Extractor.extract(line)   # Extract information

            # Handle information if existent, there should be just one information per line
            if len(information) > 0:

                parameter = information[0][0]           # Get Parameter
                value = information[0][1]               # Get Value
                
                if parameter in non_number_parameter:   # Handle parameter if non number parameter, self explaining
                    match parameter:
                        case "S_IS_ABSOLUTE":
                            if value == "0":            # 1 is default
                                self.S_IS_ABSOLUTE = False
                        case "START_POSITION_X":
                            self.START_POSITION_LINEAR_AXES[0] = float(value)
                        case "START_POSITION_Y":
                            self.START_POSITION_LINEAR_AXES[1] = float(value)
                        case "START_POSITION_Z":
                            self.START_POSITION_LINEAR_AXES[2] = float(value)
                        case "TOOL_CHANGE_POSITION_X":
                            self.TOOL_CHANGE_POSITION_LINEAR_AXES[0] = float(value)
                        case "TOOL_CHANGE_POSITION_Y":
                            self.TOOL_CHANGE_POSITION_LINEAR_AXES[1] = float(value)
                        case "TOOL_CHANGE_POSITION_Z":
                            self.TOOL_CHANGE_POSITION_LINEAR_AXES[2] = float(value)
                elif hasattr(self, parameter):          # Handle number parameter 
                    setattr(self, parameter, int(value))
                else:                                   # Handle situation that the parameter does not exist
                    print("CNC-Parameter " + parameter + " does not exist. Check file parameter.txt.")
    