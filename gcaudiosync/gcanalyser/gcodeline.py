import numpy as np
import copy
from gcaudiosync.gcanalyser.cncstatus import CNC_Status, copy_CNC_Status
from gcaudiosync.gcanalyser.cncparameter import CNC_Parameter
from gcaudiosync.gcanalyser.pausemanager import Pause_Manager
from gcaudiosync.gcanalyser.frequencymanager import Frequancy_Manager
from gcaudiosync.gcanalyser.toolchangemanager import Tool_Change_Manager
from gcaudiosync.gcanalyser.coolingmanager import Cooling_Manager
from gcaudiosync.gcanalyser.movementmanager import Movement_Manager
import gcaudiosync.gcanalyser.vectorfunctions as vecfunc

# source for the g-code interpretation: https://linuxcnc.org/docs/html/gcode/g-code.html

class G_Code_Line:

    important = False
    time = 0
    start_time = 0
    end_time = 0

    def __init__(self, 
                 index: int,
                 current_status, 
                 line_info, 
                 CNC_Parameter:CNC_Parameter,
                 Frequancy_Manager: Frequancy_Manager,
                 Pause_Manager: Pause_Manager,
                 Tool_Change_Manager: Tool_Change_Manager,
                 Cooling_Manager: Cooling_Manager,
                 Movement_Manager: Movement_Manager):

        self.index = index

        self.last_line_status: CNC_Status = copy.deepcopy(current_status)
        self.line_status: CNC_Status = copy_CNC_Status(current_status)

        while len(line_info) > 0:
            command = line_info[0][0]
            number = line_info[0][1]

            if command == "G":
                line_info.pop(0)
                self.handle_G(float(number), 
                              line_info, 
                              Pause_Manager = Pause_Manager,
                              Movement_Manager = Movement_Manager)
            elif command == "M":
                line_info.pop(0)
                self.handle_M(float(number), 
                              line_info, 
                              CNC_Parameter = CNC_Parameter, 
                              Frequancy_Manager = Frequancy_Manager, 
                              Tool_Change_Manager = Tool_Change_Manager,
                              Pause_Manager = Pause_Manager,
                              Cooling_Manager = Cooling_Manager,
                              Movement_Manager = Movement_Manager)
            elif command in ["X", "Y", "Z", "A", "B", "C", "I", "J", "K", "R"]:
                self.handle_movement_without_G(line_info,
                                               Movement_Manager = Movement_Manager)
            elif command == "S":
                line_info.pop(0)
                self.handle_S(float(number), CNC_Parameter, Frequancy_Manager)
            elif command == "F":
                line_info.pop(0)
                self.handle_F(float(number), CNC_Parameter)
            else:
                print("gcodeline found this commmand" + command + ". No action defined.")
            
    def handle_G(self, 
                 number, 
                 line_info, 
                 Pause_Manager: Pause_Manager,
                 Movement_Manager: Movement_Manager):

        # Handle different G-codes using a match statement
        match number:
            case 0 | 1:     # Rapid linear movement, Linear movement
                self.important = True
                self.line_status.active_movement = number
                self.handle_linear_movement(line_info, Movement_Manager = Movement_Manager)
            case 2 | 3:     # Arc movement CW, Arc movement CCW
                self.important = True
                self.line_status.active_movement = number
                self.line_status.info_arc[0] = number
                self.handle_arc_movement(line_info, Movement_Manager = Movement_Manager)
            case 4:         # Dwell
                self.important = True
                self.handle_g04(line_info, Pause_Manager)
            case 9:         # Exact stop in this line
                self.line_status.exact_stop = True
            case 17 | 18 | 19:    # Select XY-plane, Select XZ-plane, Select YZ-plane
                self.line_status.active_plane = int(number)
            case 20:    # Inch
                raise Exception("Please use metric system, imperial system is not supported.")
            case 21:    # mm
                pass    # Standard unit, nothing to do
            case 40 | 41 | 41.1 | 42 | 42.1:    # Cutter compensation
               self.line_status.cutter_compensation = number
            case 61:    # exact stop on for this and following lines
                self.line_status.exact_stop = True
                self.line_status.G_61_active = True
            case 64:    # exact stop off
                self.line_status.G_61_active = False
            case 90:
                self.line_status.absolute_position = True
            case 90.1:
                self.line_status.absolute_arc_center = True
            case 91:
                self.line_status.absolute_position = False
            case 91.1:    # Absolute position
                self.line_status.absolute_arc_center = False
            case _:  # Unsupported G-code
                print(f"G{number} found. No action defined.")

    def handle_M(self, number, line_info, 
                 CNC_Parameter: CNC_Parameter, 
                 Frequancy_Manager: Frequancy_Manager,
                 Tool_Change_Manager: Tool_Change_Manager,
                 Pause_Manager: Pause_Manager,
                 Cooling_Manager: Cooling_Manager,
                 Movement_Manager: Movement_Manager):

        if number == CNC_Parameter.COMMAND_ABORT:
            self.handle_abort(Pause_Manager = Pause_Manager)

        elif number == CNC_Parameter.COMMAND_QUIT:
            self.handle_quit(Pause_Manager = Pause_Manager)

        elif number == CNC_Parameter.COMMAND_PROGABORT:
            self.handle_progabort(Pause_Manager = Pause_Manager)

        elif number == CNC_Parameter.COMMAND_SPINDLE_START_CW:
            self.handle_spindle_operation("CW", Frequancy_Manager)

        elif number == CNC_Parameter.COMMAND_SPINDLE_START_CCW:
            self.handle_spindle_operation("CCW", Frequancy_Manager)

        elif number == CNC_Parameter.COMMAND_SPINDLE_OFF:
            self.handle_spindle_operation("off", Frequancy_Manager)

        elif number == CNC_Parameter.COMMAND_TOOL_CHANGE:
            self.handle_tool_change(line_info, 
                                    Tool_Change_Manager = Tool_Change_Manager,
                                    Movement_Manager = Movement_Manager)

        elif number == CNC_Parameter.COMMAND_COOLING_ON:
            self.handle_cooling_operation("on", Cooling_Manager)

        elif number == CNC_Parameter.COMMAND_COOLING_OFF:
            self.handle_cooling_operation("off", Cooling_Manager)

        elif number == CNC_Parameter.COMMAND_END_OF_PROGRAM:
            self.handle_end_of_program(Frequancy_Manager = Frequancy_Manager)

    def handle_movement_without_G(self, 
                                  line_info, 
                                  Movement_Manager: Movement_Manager):
        movement = self.line_status.active_movement
        self.important = True

        if movement in [0, 1]:
            self.handle_linear_movement(line_info, 
                                        Movement_Manager = Movement_Manager)
        else:
            self.handle_arc_movement(line_info, Movement_Manager = Movement_Manager)

    def handle_F(self, number, CNC_Parameter:CNC_Parameter):

        if number <= CNC_Parameter.F_MAX:
            self.line_status.F_value = number
        else:
            self.line_status.F_value = CNC_Parameter.F_MAX

    def handle_S(self, number, CNC_Parameter:CNC_Parameter, Frequancy_Manager: Frequancy_Manager):

        if CNC_Parameter.S_IS_ABSOLUTE:
            if number <= CNC_Parameter.S_MAX:
                new_S = number
            else:
                new_S = CNC_Parameter.S_MAX
        else:
            if number >= 100:
                raise Exception("Error in gcode line " + self.index + ": S value >= 100")
            new_S = CNC_Parameter.S_MAX * number / 100

        self.line_status.S_value = new_S
        Frequancy_Manager.new_S(self.index, new_S)

    def handle_linear_movement(self, line_info, Movement_Manager: Movement_Manager):
        
        list_index = 0

        while list_index < len(line_info):

            command = line_info[list_index][0]
            number = line_info[list_index][1]

            if command in ["X", "Y", "Z", "A", "B", "C"]:
                line_info.pop(list_index)
                
                match command:
                    case "X":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear[0] = float(number)
                        else:
                            self.line_status.position_linear[0] += float(number)
                    case "Y":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear[1] = float(number)
                        else:
                            self.line_status.position_linear[1] += float(number)
                    case "Z":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear[2] = float(number)
                        else:
                            self.line_status.position_linear[2] += float(number)
                    case "A":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation[0] = float(number)
                        else:
                            self.line_status.position_rotation[0] += float(number)
                    case "B":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation[1] = float(number)
                        else:
                            self.line_status.position_rotation[1] += float(number)
                    case "C":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation[2] = float(number)
                        else:
                            self.line_status.position_rotation[2] += float(number)
            else:
                list_index += 1

        Movement_Manager.add_linear_movement(index = self.index, 
                                             last_line_status = self.last_line_status,
                                             line_status = self.line_status)

    def handle_arc_movement(self, line_info, Movement_Manager: Movement_Manager):

        list_index = 0

        self.line_status.info_arc[1] = self.line_status.position_linear[0]
        self.line_status.info_arc[2] = self.line_status.position_linear[1]
        self.line_status.info_arc[3] = self.line_status.position_linear[2]

        while list_index < len(line_info):

            command = line_info[list_index][0]
            number = line_info[list_index][1]

            if command in ["X", "Y", "Z", "A", "B", "C", "I", "J", "K", "R", "P"]:
                line_info.pop(list_index)
                
                radius_given = False
                
                match command:
                    case "X":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear[0] = float(number)
                        else:
                            self.line_status.position_linear[0] += float(number)
                    case "Y":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear[1] = float(number)
                        else:
                            self.line_status.position_linear[1] += float(number)
                    case "Z":
                        if self.line_status.absolute_position:
                            self.line_status.position_linear[2] = float(number)
                        else:
                            self.line_status.position_linear[2] += float(number)
                    case "A":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation[0] = float(number)
                        else:
                            self.line_status.position_rotation[0] += float(number)
                    case "B":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation[1] = float(number)
                        else:
                            self.line_status.position_rotation[1] += float(number)
                    case "C":
                        if self.line_status.absolute_position:
                            self.line_status.position_rotation[2] = float(number)
                        else:
                            self.line_status.position_rotation[2] += float(number)
                    case "I":
                        if self.line_status.absolute_arc_center:
                            self.line_status.info_arc[1] = float(number)
                        else:
                            self.line_status.position_rotation[1] = self.line_status.position_linear[0] + float(number)
                    case "J":
                        if self.line_status.absolute_arc_center:
                            self.line_status.info_arc[2] = float(number)
                        else:
                            self.line_status.position_rotation[2] = self.line_status.position_linear[1] + float(number)
                    case "K":
                        if self.line_status.absolute_arc_center:
                            self.line_status.info_arc[3] = float(number)
                        else:
                            self.line_status.position_rotation[3] = self.line_status.position_linear[2] + float(number)
                    case "R":
                        radius_given = True
                        self.line_status.info_arc[4] = float(number)
                    case "P":
                        self.line_status.info_arc[5] = float(number)
            else:
                list_index += 1

        if radius_given:
            self.compute_arc_center()
        else:
            self.compute_radius()

        Movement_Manager.add_arc_movement(index = self.index, 
                                          last_line_status = self.last_line_status,
                                          line_status = self.line_status)

    def handle_g04(self, line_info, Pause_Manager: Pause_Manager):
        self.important = True

        for index, info in enumerate(line_info):
            command = info[0]
            number = info[1]

            if command == "P":
                if "." in number:
                    number = int(1000 * float(number))
                else:
                    number = int(number)
                time_found = True
                line_info.pop(index)
        if not time_found:
            raise Exception("No P value found in combination with a G04 in line " + str(self.index) + ".")
            
        self.time = number
        Pause_Manager.new_dwell(self.index, number)

    def handle_abort(self, Pause_Manager: Pause_Manager):
        self.important = True
        Pause_Manager.new_pause(self.index, 0)

    def handle_quit(self, Pause_Manager: Pause_Manager):
        self.important = True
        Pause_Manager.new_pause(self.index, 1)
    
    def handle_progabort(self, Pause_Manager: Pause_Manager):
        self.important = True
        Pause_Manager.new_pause(self.index, 2)
    
    def handle_spindle_operation(self, command: str, Frequancy_Manager: Frequancy_Manager):
        self.important = True

        if command == "off":
            self.line_status.spindle_on = False
        else:
            self.line_status.spindle_on = True
            self.line_status.spindle_direction = command
        
        Frequancy_Manager.new_Spindle_Operation(self.index, command)
        
    def handle_tool_change(self, 
                           line_info, 
                           Tool_Change_Manager: Tool_Change_Manager,
                           Movement_Manager = Movement_Manager):
        self.important = True

        for command, number in enumerate(line_info):
            if command == "T":
                tool_number = int(number)
            else:
                raise Exception("Tool change was called without T-number")
        
        self.line_status.active_tool = tool_number

        Tool_Change_Manager.new_Tool(self.index, tool_number)
        Movement_Manager.add_tool_change(self.index)
        
    def handle_cooling_operation(self, command, Cooling_Manager:Cooling_Manager):
        self.important = True

        if command == "off":
            self.line_status.cooling_on = False
        else:
            self.line_status.cooling_on = True

        Cooling_Manager.new_cooling_operation(self.index, command)
    
    def handle_end_of_program(self, Frequancy_Manager: Frequancy_Manager):
        self.important = True
        
        self.line_status.spindle_on = False
        self.line_status.program_end_reached = True

        Frequancy_Manager.new_Spindle_Operation(self.index, "off")

    def compute_arc_center(self):

        movement = self.line_status.info_arc[0]
        start_position = np.copy(self.last_line_status.position_linear)
        end_position = np.copy(self.line_status.position_linear)
        mid_point = start_position + (end_position - start_position) * 0.5
        radius = self.line_status.info_arc[4]

        if self.line_status.active_plane == 17:
            start_position[2] = 0
            mid_point[2] = 0
            start_2_mid_point = mid_point - start_position 
            
            XY_normal_vector = np.array([0.0, 0.0, 1.0])

            if (radius >= 0 and movement == 2) or (radius < 0 and movement == 3):
                direction = "right"
            elif (radius >= 0 and movement == 3) or (radius < 0 and movement == 2):
                direction = "left"
            else:
                raise Exception("Something wrong here.")

            mid_2_center = vecfunc.compute_normal_vector(start_2_mid_point, XY_normal_vector, direction)

            len_start_2_mid_point = np.linalg.norm(start_2_mid_point)

            len_mid_2_center = np.sqrt(np.power(radius, 2) - np.power(len_start_2_mid_point, 2))

            mid_2_center = mid_2_center * len_mid_2_center

            arc_center = mid_point + mid_2_center
        else:
            raise Exception("G02 and G03 are only available in plane 17 (XY)")
        
        self.line_status.info_arc[1:4] = arc_center

    def compute_radius(self):

        end_position = self.line_status.position_linear
        arc_center = self.line_status.info_arc[1:4]

        if self.line_status.active_plane == 17:
            end_position = end_position[0:2]
            arc_center = arc_center[0:2]

            radius = np.linalg.norm(end_position - arc_center)

            self.line_status.info_arc[4] = radius  
        else:
            raise Exception("G02 and G03 are only available in plane 17 (XY)")
        