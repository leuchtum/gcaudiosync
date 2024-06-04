import copy
import math

import numpy as np

import gcaudiosync.gcanalyser.vectorfunctions as vecfunc

from gcaudiosync.gcanalyser.cncparameter import CNCParameter
from gcaudiosync.gcanalyser.cncstatus import CNCStatus, copy_CNC_Status
from gcaudiosync.gcanalyser.coolingmanager import CoolingManager
from gcaudiosync.gcanalyser.frequencymanager import FrequencyManager
from gcaudiosync.gcanalyser.lineextractor import LineExtractor
from gcaudiosync.gcanalyser.movementmanager import MovementManager
from gcaudiosync.gcanalyser.pausemanager import PauseManager
from gcaudiosync.gcanalyser.toolchangemanager import ToolChangeManager

# Source for the g-code interpretation: https://linuxcnc.org/docs/html/gcode/g-code.html

class GCodeLine:

    important: bool         = False     # Is this line important for the visualisation: True or False
    #time: int               = 0         # Expexted time in ms
    indices_of_movements    = []        # Indices of the movements at the Movement_Manager

    # Constructor
    def __init__(self, 
                 line_index: int,
                 current_status: CNCStatus, 
                 line: str, 
                 Line_Extractor: LineExtractor,
                 CNC_Parameter:CNCParameter,
                 Frequency_Manager: FrequencyManager,
                 Pause_Manager: PauseManager,
                 Tool_Change_Manager: ToolChangeManager,
                 Cooling_Manager: CoolingManager,
                 Movement_Manager: MovementManager):

        self.index: int     = line_index    # Index of this line in the g-code

        self.original_line  = line          # Save original line

        line_info: list     = Line_Extractor.extract(line = line)          # Extract info from line

        self.last_line_status: CNCStatus   = copy.deepcopy(current_status)     # Save the cnc-status of the last line
        self.line_status: CNCStatus        = copy_CNC_Status(current_status)   # Create a new cnc-status for this line

        # Priorisation so the movements have all important infos
        prio_G_numbers = [9]                                        # Numbers of proi G commands
        prio_M_numbers = [CNC_Parameter.COMMAND_SPINDLE_START_CW,   # Numbers of proi M commands
                          CNC_Parameter.COMMAND_SPINDLE_START_CCW, 
                          CNC_Parameter.COMMAND_SPINDLE_OFF]

        something_to_find = True
        # Search for: new S and F values, proi G commands and prio M commands
        while something_to_find and len(line_info) > 0:
            for info_index in range(len(line_info)):
                
                # Get the command (letter) and number from line info
                command = line_info[info_index][0]
                number = line_info[info_index][1]

                match command:
                    case "F":                                                           # Action with new F value
                        line_info.pop(info_index)                                           # Delete this command and number
                        self.handle_F(float(number), CNC_Parameter)                         # Call method that handles new F value
                        break
                    case "S":                                                           # Action with a new S value
                        line_info.pop(info_index)                                           # Delete this command and number
                        self.handle_S(float(number), CNC_Parameter, Movement_Manager, Frequency_Manager)      # Call method that handles new S value
                        break
                    case "G":                                                           # Action for prio G commands
                        if float(number) in prio_G_numbers:                                 # Check if prio
                            line_info.pop(info_index)                                                    # Delete this command and number
                            self.handle_G(float(number),                                        # Call the method that handles G commands
                                          line_info, 
                                          Pause_Manager = Pause_Manager,
                                          Movement_Manager = Movement_Manager)
                            break
                    case "M":                                                           # Action for prio M commands
                        if float(number) in prio_M_numbers:                                 # Check if prio
                            line_info.pop(info_index)
                            self.handle_M(float(number),                                        # Call the method that handles M commands
                                        line_info, 
                                        CNC_Parameter = CNC_Parameter, 
                                        Frequency_Manager = Frequency_Manager, 
                                        Tool_Change_Manager = Tool_Change_Manager,
                                        Pause_Manager = Pause_Manager,
                                        Cooling_Manager = Cooling_Manager,
                                        Movement_Manager = Movement_Manager)
                            break
                
                if info_index == len(line_info)-1:
                    something_to_find = False

        # Go through rest of the info from this line and take actions
        while len(line_info) > 0:

            # Get the first command (letter) and number from line info
            command = line_info[0][0]
            number = line_info[0][1]

            # Take action for the command in charge
            if command == "N":                      # Action with line number
                line_info.pop(0)                    # Delete this command and number
            elif command == "G":                    # Action with a G command
                line_info.pop(0)                    # Delete this command and number
                self.handle_G(float(number),        # Call the method that handles G commands
                              line_info, 
                              Pause_Manager = Pause_Manager,
                              Movement_Manager = Movement_Manager)
            elif command == "M":                    # Action with a M command
                line_info.pop(0)                    # Delete this command and number
                self.handle_M(float(number),        # Call the method that handles M commands
                              line_info, 
                              CNC_Parameter = CNC_Parameter, 
                              Frequency_Manager = Frequency_Manager, 
                              Tool_Change_Manager = Tool_Change_Manager,
                              Pause_Manager = Pause_Manager,
                              Cooling_Manager = Cooling_Manager,
                              Movement_Manager = Movement_Manager)
            elif command in ["X", "Y", "Z", "A", "B", "C", "I", "J", "K", "R"]:     # Stand alone-parameter -> movement without a G command, do not delete this command and number!
                self.handle_movement_without_G(line_info,                           # Call method that handles movements without a G command
                                               Movement_Manager = Movement_Manager)
            else:                                                                           # No action defined for this command
                line_info.pop(0)                                                            # Delete this command and number
                print(f"gcodeline found this commmand: {command} in line {self.index+1}. no action defined.")  # print info
        
        self.indices_of_movements = Movement_Manager.get_indices_of_movements_for_gcode_line(self.index)   # Get movement indices 
        #self.time = Movement_Manager.get_expected_time_of_gcode_line(self.index)                 # Get expected time

    #################################################################################################
    # Methods

    # Method for all G commands
    def handle_G(self, 
                 number: float, 
                 line_info: list, 
                 Pause_Manager: PauseManager,
                 Movement_Manager: MovementManager):

        # Handle G commands
        match number:
            case 0:                             # Rapid linear movement
                self.line_status.active_movement = number                                   # Save movement
                self.line_status.feed_rate = CNCParameter.F_MAX / 60000.0                  # Set feed rate
                self.handle_linear_movement(line_info, Movement_Manager = Movement_Manager) # Call method to handle the linear movement
            case 1:                             # Linear movement   
                self.line_status.active_movement = number                                   # Save movement
                self.line_status.feed_rate = self.line_status.F_value / 60000.0             # Set feed rate
                self.handle_linear_movement(line_info, Movement_Manager = Movement_Manager) # Call method to handle the linear movement
            case 2 | 3:                         # Arc movement CW, Arc movement CCW
                self.line_status.active_movement = number                                   # Save movement
                self.line_status.arc_information.direction = number                         # Save movement in arc info
                self.line_status.feed_rate = self.line_status.F_value / 60000.0             # Set feed rate
                self.handle_arc_movement(line_info, Movement_Manager = Movement_Manager)    # Call method to handle the arc movement
            case 4:                             # Dwell
                self.handle_g04(line_info, Pause_Manager = Pause_Manager, Movement_Manager = Movement_Manager)  # Call method to handle dwell
            case 9:                             # Exact stop in this line
                self.line_status.exact_stop = True                                          # Take action
            case 17 | 18 | 19:                  # Select XY-plane, Select XZ-plane, Select YZ-plane
                self.line_status.active_plane = int(number)                                 # Take action
            case 20:                            # Length unit: Inch, not supported
                raise Exception("Please use metric system, imperial system is not supported.")  # Take action
            case 21:                            # Length unit: mm
                pass                                                                        # Standard unit, nothing to do
            case 40 | 41 | 41.1 | 42 | 42.1:    # Cutter compensation
               self.line_status.cutter_compensation = number                                # Take action
            case 61:                            # exact stop on for this and following lines
                self.line_status.exact_stop = True                                          # Take action
                self.line_status.G_61_active = True                                         # Take action
            case 64:                            # exact stop off
                self.line_status.G_61_active = False                                        # Take action
            case 90:                            # Absolute position for axes
                self.line_status.absolute_position = True                                   # Take action
            case 90.1:                          # Absolute position for arc center
                self.line_status.absolute_arc_center = True                                 # Take action
            case 91:                            # Relative position for axes
                self.line_status.absolute_position = False                                  # Take action
            case 91.1:                          # Relative position for arc center
                self.line_status.absolute_arc_center = False                                # Take action
            case _:                             # Unsupported G commands
                print(f"G{number} found. No action defined.")                               # Take action

    # Method for all M commands
    def handle_M(self, 
                 number: float, 
                 line_info: list, 
                 CNC_Parameter: CNCParameter, 
                 Frequency_Manager: FrequencyManager,
                 Tool_Change_Manager: ToolChangeManager,
                 Pause_Manager: PauseManager,
                 Cooling_Manager: CoolingManager,
                 Movement_Manager: MovementManager):

        # Handle M command, self explaining
        match number:
            case CNC_Parameter.COMMAND_ABORT:
                self.handle_abort(Pause_Manager = Pause_Manager, Movement_Manager = Movement_Manager)       # Call method
            case CNC_Parameter.COMMAND_QUIT:
                self.handle_quit(Pause_Manager = Pause_Manager, Movement_Manager = Movement_Manager)        # Call method
            case CNC_Parameter.COMMAND_PROGABORT:
                self.handle_progabort(Pause_Manager = Pause_Manager, Movement_Manager = Movement_Manager)   # Call method
            case CNC_Parameter.COMMAND_SPINDLE_START_CW:
                self.handle_spindle_operation("CW", Frequency_Manager)              # Call method
            case CNC_Parameter.COMMAND_SPINDLE_START_CCW:
                self.handle_spindle_operation("CCW", Frequency_Manager)             # Call method
            case CNC_Parameter.COMMAND_SPINDLE_OFF:
                    self.handle_spindle_operation("off", Frequency_Manager)         # Call method
            case CNC_Parameter.COMMAND_TOOL_CHANGE:
                self.handle_tool_change(line_info,                                  # Call method
                                        Tool_Change_Manager = Tool_Change_Manager,
                                        Movement_Manager = Movement_Manager)
            case CNC_Parameter.COMMAND_COOLING_ON:
                self.handle_cooling_operation("on", Cooling_Manager)                # Call method   
            case CNC_Parameter.COMMAND_COOLING_OFF:
                self.handle_cooling_operation("off", Cooling_Manager)               # Call method
            case CNC_Parameter.COMMAND_END_OF_PROGRAM:
                self.handle_end_of_program(Frequency_Manager = Frequency_Manager,   # Call method
                                           Movement_Manager = Movement_Manager)

    # Method for a movement without a G command
    def handle_movement_without_G(self, 
                                  line_info: list, 
                                  Movement_Manager: MovementManager):
        
        movement = self.line_status.active_movement     # Get active movement

        self.important = True                           # Set importance flag

        # Handle movement
        if movement in [0, 1]:                          # Linear movement
            self.handle_linear_movement(line_info,          # Call method to handle linear movement
                                        Movement_Manager = Movement_Manager)
        else:                                           # Arc movement
            self.handle_arc_movement(line_info,             # Call method to handle arc movement
                                     Movement_Manager = Movement_Manager)

    # Method for new F value
    def handle_F(self, 
                 number: float,
                 CNC_Parameter: CNCParameter):
        
        # Check number
        if number < 0:
            raise Exception(f"Error in gcode line {self.index+1}: Number for F value must be nonnegative.")

        if number <= CNC_Parameter.F_MAX:                   # Number is valid
            self.line_status.F_value = number                   # Set F value 
        else:                                               # Number is not valid
            self.line_status.F_value = CNC_Parameter.F_MAX      # Set F value to F_MAX

    # method for new S value
    def handle_S(self, 
                 number: float, 
                 CNC_Parameter: CNCParameter, 
                 Movement_Manager: MovementManager,
                 Frequency_Manager: FrequencyManager):
        
        # Check input
        if number < 0:
            raise Exception(f"Error in gcode line {self.index+1}: Number for S value must be nonnegative.")

        self.important = True                           # Set importance flag

        # Handle S value
        if CNC_Parameter.S_IS_ABSOLUTE:                 # S value is absolute
            if number <= CNC_Parameter.S_MAX:               # S value is valid
                new_S = number                                  # Set S value
            else:                                           # S value is not valid
                new_S = CNC_Parameter.S_MAX                     # Set S value to S_MAX
        else:                                           # S value is relative
            if number > 100:                                # Check if number is valid
                raise Exception(f"Error in gcode line {self.index+1}: Relative S value > 100")
            new_S = CNC_Parameter.S_MAX * number / 100.0    # Set S value

        self.line_status.S_value = new_S                # Set S value in line status
        Frequency_Manager.new_S(self.index, new_S)      # Inform Frequency Manager that S value has changed
        Movement_Manager.add_pause(self.index, 1)

    # Method for linear movement
    def handle_linear_movement(self, 
                               line_info: list, 
                               Movement_Manager: MovementManager):

        self.important = True                           # Set importanve flag

        info_index = 0                                  # Define index for line_info

        # Go through line info until everything was seen
        while info_index < len(line_info):

            command = line_info[info_index][0]              # Get command
            number = line_info[info_index][1]               # Get number

            if command in ["X", "Y", "Z", "A", "B", "C"]:   # Command is useful for this Method
                line_info.pop(info_index)                       # Remove command and number from line_info
                
                # Set the parameter to absolute value
                match command:
                    case "X":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear_axes.X = float(number)
                        else:
                            self.line_status.position_linear_axes.X += float(number)
                    case "Y":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear_axes.Y = float(number)
                        else:
                            self.line_status.position_linear_axes.Y += float(number)
                    case "Z":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear_axes.Z = float(number)
                        else:
                            self.line_status.position_linear_axes.Z += float(number)
                    case "A":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation_axes[0] = float(number)
                        else:
                            self.line_status.position_rotation_axes[0] += float(number)
                    case "B":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation_axes[1] = float(number)
                        else:
                            self.line_status.position_rotation_axes[1] += float(number)
                    case "C":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation_axes[2] = float(number)
                        else:
                            self.line_status.position_rotation_axes[2] += float(number)
            else:                                           # Command is not useful for this method
                info_index += 1                                 # Iterate info_index

        Movement_Manager.add_linear_movement(line_index = self.index,                        # Inform movement manager 
                                             last_line_status = self.last_line_status, 
                                             current_line_status = self.line_status)

    # Method for arc movement
    def handle_arc_movement(self, 
                            line_info: list, 
                            Movement_Manager: MovementManager):
        
        self.important = True       # Set importanve flag

        info_index = 0              # Define index for line_info

        self.line_status.arc_information.I = self.line_status.position_linear_axes.X      # Set I to X value
        self.line_status.arc_information.J = self.line_status.position_linear_axes.Y      # Set J to Y value
        self.line_status.arc_information.K = self.line_status.position_linear_axes.Z      # Set K to Z value

        # Go through line info until everything was seen
        while info_index < len(line_info):

            command = line_info[info_index][0]  # Get command
            number = line_info[info_index][1]   # Get number

            if command in ["X", "Y", "Z", "A", "B", "C", "I", "J", "K", "R", "P"]:  # Command is useful for this Method
                
                line_info.pop(info_index)       # Remove command and number from line_info
                
                radius_given = False            # Variable to store the information if the radius was given
                
                # Set the parameter to absolute value
                match command:
                    case "X":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear_axes.X = float(number)
                        else:
                            self.line_status.position_linear_axes.X += float(number)
                    case "Y":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear_axes.Y = float(number)
                        else:
                            self.line_status.position_linear_axes.Y += float(number)
                    case "Z":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear_axes.Z = float(number)
                        else:
                            self.line_status.position_linear_axes.Z += float(number)
                    case "A":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation_axes[0] = float(number)
                        else:
                            self.line_status.position_rotation_axes[0] += float(number)
                    case "B":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation_axes[1] = float(number)
                        else:
                            self.line_status.position_rotation_axes[1] += float(number)
                    case "C":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation_axes[2] = float(number)
                        else:
                            self.line_status.position_rotation_axes[2] += float(number)
                    case "I":
                        if self.line_status.absolute_arc_center:
                            self.line_status.arc_information.I = float(number)
                        else:
                            self.line_status.arc_information.I +=  float(number)
                    case "J":
                        if self.line_status.absolute_arc_center:
                            self.line_status.arc_information.J = float(number)
                        else:
                            self.line_status.arc_information.J += float(number)
                    case "K":
                        if self.line_status.absolute_arc_center:
                            self.line_status.arc_information.K = float(number)
                        else:
                            self.line_status.arc_information.K += float(number)
                    case "R":
                        radius_given = True
                        self.line_status.arc_information.radius = float(number)
            else:                           # Command is not useful for this Method
                info_index += 1                 # Iterate info index

        
        if radius_given:
            self.compute_arc_center()       # Compute the arc center with a given radius
        else:
            self.compute_radius()           # Compute the radius with a given arc center

        Movement_Manager.add_arc_movement(line_index = self.index,                       # Inform movement manager
                                          last_line_status = self.last_line_status, 
                                          current_line_status = self.line_status)

    # Method for dwell time
    def handle_g04(self, 
                   line_info: list, 
                   Pause_Manager: PauseManager,
                   Movement_Manager: MovementManager):
        
        self.important = True                   # Set importanve flag

        # Search for the P value, should be the first command in the line_info
        for info_index, info in enumerate(line_info):

            command = info[0]                       # Get the command
            number = info[1]                        # Get the number

            if command == "P":                      # P command found
                if "." in number:                       # P value is in s
                    number = int(1000.0 * float(number))    # Set number
                else:                                   # P value is in ms
                    number = int(number)                    # Set number

                P_value = True                          # Set flag that P value was found             
                line_info.pop(info_index)               # Remove command and number from line_info
                break                                   # Break loop
                
        # Handle Error that the P value was not found
        if not P_value:                             
            raise Exception(f"No P value found in combination with a G04 in line {self.index+1}.")
            
        Pause_Manager.new_dwell(self.index, number)     # Inform pause manager
        Movement_Manager.add_pause(self.index, number)  # Inform movement manager

    # Method for abort command
    def handle_abort(self, 
                     Pause_Manager: PauseManager, 
                     Movement_Manager: MovementManager):
        self.important = True                               # Set importance flag
        Pause_Manager.new_pause(self.index, 0)              # Inform pause manager
        Movement_Manager.add_pause(self.index, -1)          # Inform movement manager

    # Method for quit command
    def handle_quit(self, 
                    Pause_Manager: PauseManager, 
                    Movement_Manager: MovementManager):
        self.important = True                       # Set importanve flag
        Pause_Manager.new_pause(self.index, 1)      # Inform pause manager
        Movement_Manager.add_pause(self.index, -1)  # Inform movement manager
    
    # Method for progabort command
    def handle_progabort(self, 
                         Pause_Manager: PauseManager, 
                         Movement_Manager: MovementManager):
        self.important = True                           # Set importace flag
        Pause_Manager.new_pause(self.index, 2)          # Inform pause manager
        Movement_Manager.add_pause(self.index, -1)      # Inform movement manager
    
    # Method for a spindle operation
    def handle_spindle_operation(self, 
                                 command: str, 
                                 Frequency_Manager: FrequencyManager):
        
        self.important = True                                       # Set importange flag

        # Handle spindle operation
        if command == "off":                                        
            self.line_status.spindle_on = False
        else:
            self.line_status.spindle_on = True
            self.line_status.spindle_direction = command
        
        Frequency_Manager.new_Spindle_Operation(self.index, command)    # Inform frequency manager
    
    # Method for a tool change
    def handle_tool_change(self, 
                           line_info: list, 
                           Tool_Change_Manager: ToolChangeManager,
                           Movement_Manager = MovementManager):
        
        self.important = True                                           # Set importance flag

        T_value_found = False

        # Search for T value in line_info
        for info_index, info in enumerate(line_info):                        
            if info[0] == "T":                                              # T value found
                tool_number = int(info[1])                                      # Get tool number
                line_info.pop(info_index)                                       # Remove command and number from line_info
                T_value_found = True                                            # Set T_value_found True
        
        # Case: no T value found
        if not T_value_found:
            raise Exception(f"Tool change was called without T value in line {self.index}")
        
        self.line_status.active_tool = tool_number          # Set tool number

        Tool_Change_Manager.new_Tool(self.index)            # Inform tool change manager
        Movement_Manager.add_tool_change(self.index)        # Inform movement manager

    # Method for a cooling operation 
    def handle_cooling_operation(self, 
                                 command: str, 
                                 Cooling_Manager: CoolingManager):
        
        self.important = True                                       # Set importance flag

        # Handle command
        if command == "off":
            self.line_status.cooling_on = False
        else:
            self.line_status.cooling_on = True

        Cooling_Manager.new_cooling_operation(self.index, command)  # Inform cooling manager
    
    # Method for end of program command
    def handle_end_of_program(self, 
                              Frequency_Manager: FrequencyManager, 
                              Movement_Manager: MovementManager):
        
        self.important = True                                       # Set importance flag
        
        self.line_status.spindle_on = False                         # Update line status
        self.line_status.program_end_reached = True                 # Update line status

        Frequency_Manager.new_Spindle_Operation(self.index, "off")  # Inform frequency manager
        Movement_Manager.add_end_of_program(self.index)             # Inform movement manager

    # Method to compute the arc center
    def compute_arc_center(self):

        movement: int = self.line_status.arc_information.direction                     # Get the movement, 2: CW, 3: CCW
        start_position = self.last_line_status.position_linear_axes.get_as_array()     # Get the start position
        end_position = self.line_status.position_linear_axes.get_as_array()            # Get the end position

        mid_point = start_position + (end_position - start_position) * 0.5      # Compute the mid point between start and end position
        
        radius = self.line_status.arc_information.radius                        # Get the radius

        if self.line_status.active_plane == 17:                                 # Active plane is the XY-plane
            
            Z_position = start_position[2]                                      # Save Z position
            start_position[2] = 0.0                                             # Set Z value of start position to 0
            mid_point[2] = 0.0                                                  # Set Z value of end position to 0

            start_2_mid_point = mid_point - start_position                      # Compute vector from start to mid point
            
            XY_normal_vector = np.array([0.0, 0.0, 1.0])                        # Create normal vector from XY-plane

            # Get the direction of the location of the arc-center
            if (radius >= 0 and movement == 2) or (radius < 0 and movement == 3):
                direction = "right"
            elif (radius >= 0 and movement == 3) or (radius < 0 and movement == 2):
                direction = "left"
            else:
                raise Exception("Something wrong here LOL.")

            mid_2_center = vecfunc.compute_normal_vector(vec1 = start_2_mid_point,  # Compute direction from mid point to arc center
                                                         vec2 = XY_normal_vector, 
                                                         direction = direction)

            len_start_2_mid_point = np.linalg.norm(start_2_mid_point)               # Compute distance from start to mid point

            len_mid_2_center = math.sqrt(math.pow(radius, 2) - math.pow(len_start_2_mid_point, 2))  # Compute distance from mid point to center

            mid_2_center = mid_2_center * len_mid_2_center      # Adjust the length of the vector from mid to center

            arc_center = mid_point + mid_2_center               # Compute arc center
        
            arc_center[2] = Z_position                      # Set z position
        else:                                               # Active plane is not XY-plane
            raise Exception("G02 and G03 are only available in plane 17 (XY)")
        
        self.line_status.arc_information.set_arc_center(arc_center)         # Set arc center

    # method to compute the radius
    def compute_radius(self):

        end_position = self.line_status.position_linear_axes.get_as_array()         # Get end position
        arc_center = self.line_status.arc_information.get_arc_center_as_array()     # Get arc center

        if self.line_status.active_plane == 17:                                     # Check if XY-plane is active

            radius = np.linalg.norm(end_position - arc_center)                      # Compute radius

            self.line_status.arc_information.radius = radius                               # Set radius
            
        else:                                                                   # XY-plane is not active
            raise Exception("G02 and G03 are only available in plane 17 (XY)")

# End of class
#####################################################################################################
