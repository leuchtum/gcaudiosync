from gcaudiosync.gcanalyser.filefunctions import *
from gcaudiosync.gcanalyser.linearaxes import LinearAxes
from gcaudiosync.gcanalyser.lineextractor import LineExtractor
from gcaudiosync.gcanalyser.rotationaxes import RotationAxes

class CNCParameter:
    """
    Represents the parameters of a CNC machine.

    This class stores various parameters used in CNC machining operations.

    Attributes:
        START_POSITION_LINEAR_AXES (LinearAxes): The starting position of the linear axes.
        START_POSITION_ROTATION_AXES (RotationAxes): The starting position of the rotation axes.
        TOOL_CHANGE_POSITION_LINEAR_AXES (LinearAxes): The position for tool changes.
        S_IS_ABSOLUTE (bool): Flag indicating whether the S value is absolute.
        F_MAX (float): Maximum feed rate in mm/min.
        S_MAX (float): Maximum spindle speed in RPM.
        MAX_A_X (float): Maximum acceleration/deceleration of the X-Axis in mm/s^2.
        MAX_A_Y (float): Maximum acceleration/deceleration of the Y-Axis in mm/s^2.
        MAX_A_Z (float): Maximum acceleration/deceleration of the Z-Axis in mm/s^2.
        TOOL_CHANGE_TIME (int): Time taken for a tool change in milliseconds.
        COMMAND_ABORT (float): M command for aborting.
        COMMAND_QUIT (float): M command for quitting.
        COMMAND_PROGABORT (float): M command for program abort.
        COMMAND_SPINDLE_START_CW (float): M command for starting spindle clockwise.
        COMMAND_SPINDLE_START_CCW (float): M command for starting spindle counterclockwise.
        COMMAND_SPINDLE_OFF (float): M command for turning off spindle.
        COMMAND_TOOL_CHANGE (float): M command for tool change.
        COMMAND_COOLING_ON (float): M command for turning on cooling.
        COMMAND_COOLING_OFF (float): M command for turning off cooling.
        COMMAND_END_OF_PROGRAM (float): M command for end of program.
    """
    
    # Class variables

    # Machine parameter
    START_POSITION_LINEAR_AXES          = LinearAxes(100.0, 100.0, 100.0)
    START_POSITION_ROTATION_AXES        = RotationAxes()
    TOOL_CHANGE_POSITION_LINEAR_AXES    = LinearAxes(100.0, 100.0, 100.0)

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
        """
        Initializes the CNCParameter object.

        Args:
            parameter_src (str, optional): The source of the CNC parameters. Defaults to "".
        """

        # Get the parameter from the parameter list
        parameter: str = read_file(parameter_src)    

        # Make an Extractor
        Extractor: LineExtractor = LineExtractor()

        # No src for cnc-parameter given
        if len(parameter) == 0:
            print("Using default CNC-parameter.")

        # Non number parameter
        non_number_parameter = [
            "S_IS_ABSOLUTE",
            "START_POSITION_X",
            "START_POSITION_Y",
            "START_POSITION_Z",
            "TOOL_CHANGE_POSITION_X",
            "TOOL_CHANGE_POSITION_Y",
            "TOOL_CHANGE_POSITION_Z",
        ]

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
                            self.START_POSITION_LINEAR_AXES.X = float(value)
                        case "START_POSITION_Y":
                            self.START_POSITION_LINEAR_AXES.Y = float(value)
                        case "START_POSITION_Z":
                            self.START_POSITION_LINEAR_AXES.Z = float(value)
                        case "TOOL_CHANGE_POSITION_X":
                            self.TOOL_CHANGE_POSITION_LINEAR_AXES.X = float(value)
                        case "TOOL_CHANGE_POSITION_Y":
                            self.TOOL_CHANGE_POSITION_LINEAR_AXES.Y = float(value)
                        case "TOOL_CHANGE_POSITION_Z":
                            self.TOOL_CHANGE_POSITION_LINEAR_AXES.Z = float(value)
                elif hasattr(self, parameter):          # Handle number parameter 
                    setattr(self, parameter, int(value))
                else:                                   # Handle situation that the parameter does not exist
                    print("CNC-Parameter " + parameter + " does not exist. Check file parameter.txt.")

    #################################################################################################
    # Methods

# End of class
#####################################################################################################
