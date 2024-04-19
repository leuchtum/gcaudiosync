import numpy as np

from gcaudiosync.gcanalyser.lineextractor import LineExtractor
from gcaudiosync.gcanalyser.filefunctions import *

class CNC_Parameter:
    
    # Machine parameter
    START_POSITION = np.array([100.0, 100.0, 100.0])
    TOOL_CHANGE_POSITION = np.array([100.0, 100.0, 100.0])

    S_IS_ABSOLUTE = True

    F_MAX = 20000       # max feed rate in mm/min
    S_MAX = 18000       # max spindle speed in RPM

    MAX_A_X = 40        # max acceleration/deceleration of X-Axis in mm/s^2
    MAX_A_Y = 40        # max acceleration/deceleration of Y-Axis in mm/s^2
    MAX_A_Z = 40        # max acceleration/deceleration of Z-Axis in mm/s^2

    TOOL_CHANGE_TIME = 8000     # [ms]

    COMMAND_ABORT = 0
    COMMAND_QUIT = 1
    COMMAND_PROGABORT = 2
    COMMAND_SPINDLE_START_CW = 3
    COMMAND_SPINDLE_START_CCW = 4
    COMMAND_SPINDLE_OFF = 5
    COMMAND_TOOL_CHANGE = 6
    COMMAND_COOLING_ON = 8
    COMMAND_COOLING_OFF = 9
    COMMAND_END_OF_PROGRAM = 30

    # Constructor
    def __init__(self, parameter_src):

        parameter = read_file(parameter_src)
        Extractor = LineExtractor()

        if len(parameter) == 0:
            print("Problem with cnc-parameter file. Using default values.")
            return None

        non_int_parameter = ["S_IS_ABSOLUTE",
                             "START_POSITION_X",
                             "START_POSITION_Y",
                             "START_POSITION_Z",
                             "TOOL_CHANGE_POSITION_X",
                             "TOOL_CHANGE_POSITION_Y",
                             "TOOL_CHANGE_POSITION_Z",]

        for line in parameter:
            information = Extractor.extract(line)
            if len(information) > 0:
                parameter = information[0][0]
                value = information[0][1]
                
                if parameter in non_int_parameter:
                    match parameter:
                        case "S_IS_ABSOLUTE":
                            if value == "0":
                                self.S_IS_ABSOLUTE = False
                        case "START_POSITION_X":
                            self.START_POSITION[0] = float(value)
                        case "START_POSITION_Y":
                            self.START_POSITION[1] = float(value)
                        case "START_POSITION_Z":
                            self.START_POSITION[2] = float(value)
                        case "TOOL_CHANGE_POSITION_X":
                            self.TOOL_CHANGE_POSITION[0] = float(value)
                        case "TOOL_CHANGE_POSITION_Y":
                            self.TOOL_CHANGE_POSITION[1] = float(value)
                        case "TOOL_CHANGE_POSITION_Z":
                            self.TOOL_CHANGE_POSITION[2] = float(value)
                elif hasattr(self, parameter):
                    setattr(self, parameter, int(value))
                else:
                    print("CNC-Parameter " + parameter + " does not exist. Check file parameter.txt.")

        return None
    