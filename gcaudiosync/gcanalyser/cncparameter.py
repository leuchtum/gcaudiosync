import numpy as np

from gcaudiosync.gcanalyser.filefunctions import *
from gcaudiosync.gcanalyser.linearaxes import LinearAxes
from gcaudiosync.gcanalyser.lineextractor import LineExtractor
from gcaudiosync.gcanalyser.rotationaxes import RotationAxes

class CNCParameter:
    """
    Represents the parameters of a CNC machine. Stores various parameters used in CNC machining operations.

    Attributes:
    -----------
    START_POSITION_LINEAR_AXES : LinearAxes
        The starting position of the linear axes.
    START_POSITION_ROTATION_AXES : RotationAxes
        The starting position of the rotation axes.
    TOOL_CHANGE_POSITION_LINEAR_AXES : LinearAxes)
        The position for tool changes.
    S_IS_ABSOLUTE : bool
        Flag indicating whether the S value is absolute.
    F_MAX : float
        Maximum feed rate in mm/min.
    S_MAX : float
        Maximum spindle speed in RPM.
    MAX_ACCELERATION_X : float
        Maximum acceleration of the X-Axis in mm/s^2.
    MAX_ACCELERATION_Y : float
        Maximum acceleration of the Y-Axis in mm/s^2.
    MAX_ACCELERATION_Z : float
        Maximum acceleration of the Z-Axis in mm/s^2.
    MAX_DECELERATION_X : float
        Maximum deceleration of the X-Axis in mm/s^2.
    MAX_DECELERATION_Y : float
        Maximum deceleration of the Y-Axis in mm/s^2.
    MAX_DECELERATION_Z : float
        Maximum deceleration of the Z-Axis in mm/s^2.
    DEFAULT_PAUSE_TIME : float
        Default time for a pause in ms.
    TOOL_CHANGE_TIME : float
        Time taken for a tool change in milliseconds.
    COMMAND_ABORT : float
        M command for aborting.
    COMMAND_QUIT : float
        M command for quitting.
    COMMAND_PROGABORT : float
        M command for program abort.
    COMMAND_SPINDLE_START_CW : float
        M command for starting spindle clockwise.
    COMMAND_SPINDLE_START_CCW : float
        M command for starting spindle counterclockwise.
    COMMAND_SPINDLE_OFF : float
        M command for turning off spindle.
    COMMAND_TOOL_CHANGE : float
        M command for tool change.
    COMMAND_COOLING_ON : float
        M command for turning on cooling.
    COMMAND_COOLING_OFF : float
        M command for turning off cooling.
    COMMAND_END_OF_PROGRAM : float
        M command for end of program.
    """
    
    # Constructor
    def __init__(self, 
                 parameter_src: str = ""):
        """
        Initializes the CNCParameter object.

        Parameters:
        -----------
        parameter_src : str, optional
            The source of the CNC parameters. Defaults to "".
        """

        # Machine parameter
        self.START_POSITION_LINEAR_AXES: LinearAxes       = LinearAxes(100.0, 100.0, 100.0)
        self.START_POSITION_ROTATION_AXES: RotationAxes   = RotationAxes()
        self.TOOL_CHANGE_POSITION_LINEAR_AXES: LinearAxes = LinearAxes(100.0, 100.0, 100.0)

        self.S_IS_ABSOLUTE: bool = True          # True if S value is absolute

        self.F_MAX: float = 20000.0              # max feed rate in mm/min
        self.S_MAX: float = 18000.0              # max spindle speed in RPM

        self.MAX_ACCELERATION_X: float = 0.004   # Maximum acceleration of the X-Axis in mm/ms^2.
        self.MAX_ACCELERATION_Y: float = 0.004   # Maximum acceleration of the Y-Axis in mm/ms^2.
        self.MAX_ACCELERATION_Z: float = 0.004   # Maximum acceleration of the Z-Axis in mm/ms^2.
        self.MAX_DECELERATION_X: float = 0.004   # Maximum deceleration of the X-Axis in mm/ms^2.
        self.MAX_DECELERATION_Y: float = 0.004   # Maximum deceleration of the Y-Axis in mm/ms^2.
        self.MAX_DECELERATION_Z: float = 0.004   # Maximum deceleration of the Z-Axis in mm/ms^2.

        self.DEFAULT_PAUSE_TIME: float = 5000.0  # Time for a pause in ms.
        self.TOOL_CHANGE_TIME: float   = 3000.0  # Time for a tool change in ms.

        # M commands
        self.COMMAND_ABORT: float                = 0.0
        self.COMMAND_QUIT : float                = 1.0
        self.COMMAND_PROGABORT: float            = 2.0
        self.COMMAND_SPINDLE_START_CW: float     = 3.0
        self.COMMAND_SPINDLE_START_CCW: float    = 4.0
        self.COMMAND_SPINDLE_OFF: float          = 5.0
        self.COMMAND_TOOL_CHANGE: float          = 6.0
        self.COMMAND_COOLING_ON: float           = 8.0
        self.COMMAND_COOLING_OFF: float          = 9.0
        self.COMMAND_END_OF_PROGRAM: float       = 30.0

        # No src for cnc-parameter given -> using defaults
        if parameter_src == "":
            print("Using default CNC-parameter.")
            return

        # Get the parameter from the parameter list
        parameter: str = read_file(parameter_src)    

        # Make an Extractor
        Extractor: LineExtractor = LineExtractor()

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

        # Parameter for acceleration and deceleration
        all_acc_dec = [
            "MAX_ACCELERATION_X",
            "MAX_ACCELERATION_Y",
            "MAX_ACCELERATION_Z",
            "MAX_DECELERATION_X",
            "MAX_DECELERATION_Y",
            "MAX_DECELERATION_Z",
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
                    if parameter in all_acc_dec:
                        value = abs(float(value) / 1000.0)
                    setattr(self, parameter, float(value))
                else:                                   # Handle situation that the parameter does not exist
                    print("CNC-Parameter " + parameter + " does not exist. Check file parameter.txt.")

    #################################################################################################
    # Methods

    def get_acceleration_as_array(self) -> np.array:
        """
        Gives back the accelerations of the linear axes.

        Returns:
        --------
        np.array: Acceleration of the linear axes.
        """

        max_A_X = self.MAX_ACCELERATION_X
        max_A_Y = self.MAX_ACCELERATION_Y
        max_A_Z = self.MAX_ACCELERATION_Z

        return np.array([max_A_X, max_A_Y, max_A_Z])
    
    def get_deceleration_as_array(self) -> np.array:
        """
        Gives back the decelerations of the linear axes.

        Returns:
        --------
        np.array: Deceleration of the linear axes.
        """
        
        max_D_X = self.MAX_DECELERATION_X
        max_D_Y = self.MAX_DECELERATION_Y
        max_D_Z = self.MAX_DECELERATION_Z

        return np.array([max_D_X, max_D_Y, max_D_Z])
    
# End of class
#####################################################################################################
