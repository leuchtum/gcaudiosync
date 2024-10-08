import copy
import math

import numpy as np

from typing import List, Tuple

import gcaudiosync.gcanalyser.vectorfunctions as vecfunc
import gcaudiosync.gcanalyser.cncstatus as cnc_status_operations

from gcaudiosync.gcanalyser.cncparameter import CNCParameter
from gcaudiosync.gcanalyser.cncstatus import CNCStatus
from gcaudiosync.gcanalyser.lineextractor import LineExtractor
from gcaudiosync.gcanalyser.movementmanager import MovementManager
from gcaudiosync.gcanalyser.syncinfomanager import SyncInfoManager

class GCodeLine:
    """
    Represents a single line of G-code and processes it to update CNC status and manage movements.

    Source for the G-code interpretation: https://linuxcnc.org/docs/html/gcode/g-code.html

    Attributes:
    -----------
    g_code_line_index : int
        Index of this line in the G-code file.
    original_g_code_line : str
        Original G-code line as a string.
    cnc_status_last_line : CNCStatus
        The CNC status before processing this line.
    cnc_status_current_line : CNCStatus
        The CNC status after processing this line.
    movement_indices : List[int]
        Indices of the movements in the Movement Manager.
    """

    # Constructor
    def __init__(self, 
                 g_code_line_index: int,
                 current_cnc_status: CNCStatus, 
                 g_code_line: str, 
                 Line_Extractor: LineExtractor,
                 CNC_Parameter: CNCParameter,
                 Sync_Info_Manager: SyncInfoManager,
                 Movement_Manager: MovementManager):
        """
        Initializes the GCodeLine object.

        Parameters:
        -----------
        g_code_line_index : int
            Index of this line in the G-code file.
        current_cnc_status : CNCStatus
            The current status of the CNC machine.
        g_code_line : str
            The G-code line as a string.
        Line_Extractor : LineExtractor
            An instance of the LineExtractor class.
        CNC_Parameter : CNCParameter
            An instance of the CNCParameter class.
        Sync_Info_Manager: SyncInfoManager
            An inctance of the SyncInfoManager class.
        Movement_Manager : MovementManager
            An instance of the MovementManager class.
        """

        self.movement_indices: List[int] = []               # Indices of the movements at the Movement_Manager

        self.g_code_line_index: int = g_code_line_index     # Index of this line in the g-code
        self.original_g_code_line: str   = g_code_line      # Save original line

        g_code_line_info: List[Tuple[str, str]] = Line_Extractor.extract(line = g_code_line)        # Extract info from line

        self.cnc_status_last_line: CNCStatus    = copy.deepcopy(current_cnc_status)                 # Save the cnc-status of the last line
        self.cnc_status_current_line: CNCStatus = cnc_status_operations.copy_CNC_Status(CNC_Status = current_cnc_status)  # Create a new cnc-status for this line

        # Prioritization so the movements have all important infos
        prio_G_numbers = [9, 17, 18, 19]                            # Numbers of priority G commands
        prio_M_numbers = [CNC_Parameter.COMMAND_SPINDLE_START_CW,   # Numbers of priority M commands
                          CNC_Parameter.COMMAND_SPINDLE_START_CCW, 
                          CNC_Parameter.COMMAND_SPINDLE_OFF]

        something_to_find = True
        # Search for: new S and F values, proi G commands and prio M commands
        # TODO: this loop might be improveable
        while something_to_find and len(g_code_line_info) > 0:          
            for info_index in range(len(g_code_line_info)):
                
                # Get the command (letter) and number from line info
                command = g_code_line_info[info_index][0]
                number = g_code_line_info[info_index][1]
                
                # Process the command
                match command:
                    case "F":
                        g_code_line_info.pop(info_index)                    # Delete this command and number

                        # Call method that handles new F value
                        self.handle_F(F_value = float(number), 
                                      CNC_Parameter = CNC_Parameter)         
                        break
                    case "S":
                        g_code_line_info.pop(info_index)                    # Delete this command and number

                        # Call method that handles new S value
                        self.handle_S(S_value = float(number),                        
                                      CNC_Parameter = CNC_Parameter, 
                                      Sync_Info_Manager = Sync_Info_Manager)    
                        break
                    case "G":
                        if float(number) in prio_G_numbers:                 # Check if priority
                            g_code_line_info.pop(info_index)                    # Delete this command and number+

                            # Call the method that handles G commands
                            self.handle_G(number_for_command = float(number),                        
                                          g_code_line_info = g_code_line_info, 
                                          CNC_Parameter = CNC_Parameter,
                                          Sync_Info_Manager = Sync_Info_Manager,
                                          Movement_Manager = Movement_Manager)
                            break
                    case "M":
                        if float(number) in prio_M_numbers:                 # Check if priority
                            g_code_line_info.pop(info_index)                    # Delete this command and number

                            # Call the method that handles M commands
                            self.handle_M(number_for_command = float(number),                       
                                          g_code_line_info = g_code_line_info, 
                                          CNC_Parameter = CNC_Parameter, 
                                          Sync_Info_Manager = Sync_Info_Manager,
                                          Movement_Manager = Movement_Manager)
                            break
                
                if info_index == len(g_code_line_info)-1:
                    something_to_find = False

        stand_alone_parameter = ["X", "Y", "Z", "A", "B", "C", "I", "J", "K", "R"]   # define stand alone parameter

        # Go through rest of the info from this line and take actions
        while len(g_code_line_info) > 0:

            # Get the first command (letter) and number from line info
            command: str = g_code_line_info[0][0]
            number:str = g_code_line_info[0][1]

            # Take action for the command in charge
            if command == "N":
                g_code_line_info.pop(0)                         # Delete this command and number - no further action with this at the moment
            elif command == "G":
                g_code_line_info.pop(0)                         # Delete this command and number
                # Call the method that handles G commands
                self.handle_G(number_for_command = float(number),                    
                              g_code_line_info = g_code_line_info, 
                              CNC_Parameter = CNC_Parameter,
                              Sync_Info_Manager = Sync_Info_Manager,
                              Movement_Manager = Movement_Manager)
            elif command == "M":
                g_code_line_info.pop(0)                         # Delete this command and number
                # Call the method that handles M commands
                self.handle_M(number_for_command = float(number),                    
                              g_code_line_info = g_code_line_info, 
                              CNC_Parameter = CNC_Parameter, 
                              Sync_Info_Manager = Sync_Info_Manager,
                              Movement_Manager = Movement_Manager)
            elif command in stand_alone_parameter:     # Stand alone-parameter -> movement without a G command, do not delete this command and number!
                # Call method that handles movements without a G command
                self.handle_movement_without_G(g_code_line_info = g_code_line_info,                           
                                               Movement_Manager = Movement_Manager)
            else:                                                                           # No action defined for this command
                g_code_line_info.pop(0)                                                            # Delete this command and number
                print(f"gcodeline found this commmand: {command} in line {self.g_code_line_index+1}. no action defined.")  # print info
        
        self.movement_indices = Movement_Manager.get_indices_of_movements_for_gcode_line(self.g_code_line_index)   # Get movement indices 

    #################################################################################################
    # Methods

    def handle_G(self, 
                 number_for_command: float, 
                 g_code_line_info: List[Tuple[str, str]], 
                 CNC_Parameter: CNCParameter,
                 Sync_Info_Manager: SyncInfoManager,
                 Movement_Manager: MovementManager) -> None:
        """
        Handles the G-code commands.

        Parameters:
        -----------
        number_for_command : float
            The G-code command number.
        g_code_line_info : List[Tuple[str, str]
            The remaining parts of the G-code line after extracting the command.
        Sync_Info_Manager: SyncInfoManager
            An instance of the SyncInfoManager class to handle sync informations.
        Movement_Manager : MovementManager
            An instance of the MovementManager class to handle movements.
        """

        # Handle G command
        match number_for_command:
            case 0: # Rapid linear movement
                self.cnc_status_current_line.active_movement_type = number_for_command                      # Save movement
                self.cnc_status_current_line.feed_rate = CNC_Parameter.F_MAX / 60000.0                      # Set feed rate in [mm/ms]
                # Call method to handle the linear movement
                self.handle_linear_movement(g_code_line_info = g_code_line_info,                            
                                            Movement_Manager = Movement_Manager)          
            case 1: # Linear movement   
                self.cnc_status_current_line.active_movement_type = number_for_command                      # Save movement
                self.cnc_status_current_line.feed_rate = self.cnc_status_current_line.F_value / 60000.0     # Set feed rate in [mm/ms]
                # Call method to handle the linear movement
                self.handle_linear_movement(g_code_line_info = g_code_line_info,                            
                                            Movement_Manager = Movement_Manager)
            case 2 | 3: # Arc movement CW or Arc movement CCW
                self.cnc_status_current_line.active_movement_type = number_for_command                      # Save movement
                self.cnc_status_current_line.arc_information.direction = number_for_command                 # Save movement in arc info
                self.cnc_status_current_line.feed_rate = self.cnc_status_current_line.F_value / 60000.0     # Set feed rate in [mm/ms]
                # Call method to handle the arc movement
                self.handle_arc_movement(g_code_line_info = g_code_line_info,                              
                                         Movement_Manager = Movement_Manager)
            case 4: # Dwell
                # Call method to handle dwell
                self.handle_g04(g_code_line_info = g_code_line_info,                                        
                                Sync_Info_Manager = Sync_Info_Manager, 
                                Movement_Manager = Movement_Manager)
            case 9: # Exact stop in this line
                self.cnc_status_current_line.exact_stop = True
            case 17 | 18 | 19: # Select XY-plane or Select XZ-plane or Select YZ-plane
                self.cnc_status_current_line.active_plane = int(number_for_command)
            case 20: # Length unit: Inch, not supported
                raise Exception(f"Please use metric system, imperial system is not supported.")
            case 21: # Length unit: mm
                pass                                                                        # Standard unit, nothing to do
            case 40 | 41 | 41.1 | 42 | 42.1: # Cutter compensation          # TODO: this may be better with proirisation
                self.cnc_status_current_line.cutter_compensation = number_for_command
            case 61: # exact stop on for this and following lines
                self.cnc_status_current_line.exact_stop = True                                         
                self.cnc_status_current_line.G_61_active = True
            case 64: # exact stop off
                self.cnc_status_current_line.G_61_active = False
            case 90: # Absolute position for axes
                self.cnc_status_current_line.absolute_position = True
            case 90.1: # Absolute position for arc center
                self.cnc_status_current_line.absolute_arc_center = True
            case 91: # Relative position for axes
                self.cnc_status_current_line.absolute_position = False
            case 91.1: # Relative position for arc center
                self.cnc_status_current_line.absolute_arc_center = False 
            case _: # Unsupported G commands
                print(f"G{number_for_command} found. No action defined.")

    def handle_M(self, 
                 number_for_command: float, 
                 g_code_line_info: List[Tuple[str, str]], 
                 CNC_Parameter: CNCParameter, 
                 Sync_Info_Manager: SyncInfoManager,
                 Movement_Manager: MovementManager) -> None:
        """
        Handles the M-code commands.

        Parameters:
        -----------
        number : float
            The M-code command number.
        g_code_line_info : List[Tuple[str, str]
            The remaining parts of the G-code line after extracting the command.
        CNC_Parameter : CNCParameter
            An instance of the CNCParameter class containing CNC parameters.
        Sync_Info_Manager: SyncInfoManager
            An instance of the SyncInfoManager class to handle sync info.
        Movement_Manager : MovementManager
            An instance of the MovementManager class to handle movements.
        """

        # Handle M command, self explaining
        match number_for_command:
            case CNC_Parameter.COMMAND_ABORT:
                self.handle_abort(Sync_Info_Manager = Sync_Info_Manager, 
                                  Movement_Manager = Movement_Manager)
            case CNC_Parameter.COMMAND_QUIT:
                self.handle_quit(Sync_Info_Manager = Sync_Info_Manager, 
                                 Movement_Manager = Movement_Manager)
            case CNC_Parameter.COMMAND_PROGABORT:
                self.handle_progabort(Sync_Info_Manager = Sync_Info_Manager, 
                                      Movement_Manager = Movement_Manager)
            case CNC_Parameter.COMMAND_SPINDLE_START_CW:
                self.handle_spindle_operation(spindle_command = "CW", 
                                              Sync_Info_Manager = Sync_Info_Manager)
            case CNC_Parameter.COMMAND_SPINDLE_START_CCW:
                self.handle_spindle_operation(spindle_command = "CCW", 
                                              Sync_Info_Manager = Sync_Info_Manager)
            case CNC_Parameter.COMMAND_SPINDLE_OFF:
                    self.handle_spindle_operation(spindle_command = "off", 
                                                  Sync_Info_Manager = Sync_Info_Manager)
            case CNC_Parameter.COMMAND_TOOL_CHANGE:
                self.handle_tool_change(g_code_line_info = g_code_line_info,
                                        CNC_Parameter = CNC_Parameter,
                                        Sync_Info_Manager = Sync_Info_Manager,
                                        Movement_Manager = Movement_Manager)
            case CNC_Parameter.COMMAND_COOLING_ON:
                self.handle_cooling_operation(cooling_command = "on", 
                                              Sync_Info_Manager = Sync_Info_Manager) 
            case CNC_Parameter.COMMAND_COOLING_OFF:
                self.handle_cooling_operation(cooling_command = "off", 
                                              Sync_Info_Manager = Sync_Info_Manager)
            case CNC_Parameter.COMMAND_END_OF_PROGRAM:
                self.handle_end_of_program(Sync_Info_Manager = Sync_Info_Manager,
                                           Movement_Manager = Movement_Manager)

    def handle_movement_without_G(self, 
                                  g_code_line_info: List[Tuple[str, str]], 
                                  Movement_Manager: MovementManager) -> None:
        """
        Handles movement commands without an explicit G-code.

        Parameters:
        -----------
        g_code_line_info : List[Tuple[str, str]]
            The remaining parts of the G-code line after extracting the command.
        Movement_Manager : MovementManager
            An instance of the MovementManager class to handle movements.
        """

        movement_type = self.cnc_status_current_line.active_movement_type     # Get active movement

        # Handle movement
        if movement_type in [0, 1]: # Linear movement
            self.handle_linear_movement(g_code_line_info = g_code_line_info,           # Call method to handle linear movement
                                        Movement_Manager = Movement_Manager)
        else: # Arc movement
            self.handle_arc_movement(g_code_line_info = g_code_line_info,              # Call method to handle arc movement
                                     Movement_Manager = Movement_Manager)

    def handle_F(self, 
                 F_value: float,
                 CNC_Parameter: CNCParameter) -> None:
        """
        Handles setting the feed rate (F value) in the G-code line.

        Parameters:
        -----------
        number : float
            The feed rate value to be set.
        CNC_Parameter : CNCParameter
            An instance of the CNCParameter class containing CNC parameters.
        
        Raises:
        -------
        Exception
            If the feed rate value is negative.
        """

        # Check if the number is nonnegative
        if F_value < 0:
            raise Exception(f"Error in gcode line {self.g_code_line_index+1}: Number for F value must be nonnegative.")

        # Validate the feed rate value against the maximum allowed feed rate
        if F_value <= CNC_Parameter.F_MAX:
            self.cnc_status_current_line.F_value = F_value                   # Set F value 
        else:
            self.cnc_status_current_line.F_value = CNC_Parameter.F_MAX      # Set F value to F_MAX

    def handle_S(self, 
                 S_value: float, 
                 CNC_Parameter: CNCParameter,
                 Sync_Info_Manager: SyncInfoManager) -> None:
        """
        Handles setting the spindle speed (S value) in the G-code line.

        Parameters:
        -----------
        S_value : float
            The spindle speed value to be set.
        CNC_Parameter : CNCParameter
            An instance of the CNCParameter class containing CNC parameters.
        Frequency_Manager : FrequencyManager
            An instance of the FrequencyManager class to manage frequency-related operations.
        
        Raises:
        -------
        Exception
            If the spindle speed value is negative or invalid based on CNC parameters.
        """

        # Check if the S value is nonnegative
        if S_value < 0:
            raise Exception(f"Error in gcode line {self.g_code_line_index+1}: Number for S value must be nonnegative.")

        # Determine and set the new S value based on CNC parameters
        new_S: float = 0
        if CNC_Parameter.S_IS_ABSOLUTE:
            # S value is absolute
            if S_value <= CNC_Parameter.S_MAX:
                new_S = S_value                                     # Set the valid S value
            else:
                new_S = CNC_Parameter.S_MAX
        else: 
            # S value is relative
            if S_value > 100:
                raise Exception(f"Error in gcode line {self.g_code_line_index+1}: Relative S value > 100")
            new_S = CNC_Parameter.S_MAX * S_value / 100.0           # Set the valid S value

        # Update the current line's CNC status with the new S value
        self.cnc_status_current_line.S_value = new_S

        # Inform the Frequency Manager that the S value has changed
        Sync_Info_Manager.new_S(g_code_line_index = self.g_code_line_index, 
                                new_S_value = new_S)

    def handle_linear_movement(self, 
                               g_code_line_info: List[Tuple[str, str]], 
                               Movement_Manager: MovementManager) -> None:
        """
        Handles linear movements specified in the G-code line.

        Parameters:
        -----------
        g_code_line_info : List[Tuple[str, str]]
            List of tuples where each tuple contains a command (letter) and a corresponding value.
        Movement_Manager : MovementManager
            An instance of the MovementManager class to manage movements.
        """

        g_code_line_info_index = 0  # Define index for g_code_line_info

        relevant_commands = ["X", "Y", "Z", "A", "B", "C"]  # relevant commands for linear movement

        # Iterate through line info until all commands are processed
        while g_code_line_info_index < len(g_code_line_info):

            command: str = g_code_line_info[g_code_line_info_index][0]               # Get command
            number_for_command: str = g_code_line_info[g_code_line_info_index][1]    # Get number

            if command in relevant_commands:                    # Check if command is relevant for this method
                g_code_line_info.pop(g_code_line_info_index)    # Remove command and number from g_code_line_info
                
                # Set the parameter to absolute value
                match command:
                    case "X":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_linear_axes.X = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_linear_axes.X += float(number_for_command)
                    case "Y":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_linear_axes.Y = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_linear_axes.Y += float(number_for_command)
                    case "Z":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_linear_axes.Z = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_linear_axes.Z += float(number_for_command)
                    case "A":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_rotation_axes.A = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_rotation_axes.A += float(number_for_command)
                    case "B":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_rotation_axes.B = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_rotation_axes.B += float(number_for_command)
                    case "C":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_rotation_axes.C = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_rotation_axes.C += float(number_for_command)
            else:                                               # Command is not useful for this method
                g_code_line_info_index += 1                         # Iterate g_code_line_info_index

        Movement_Manager.add_linear_movement(g_code_line_index = self.g_code_line_index,               # Inform movement manager 
                                             last_line_status = self.cnc_status_last_line, 
                                             current_line_status = self.cnc_status_current_line)

    def handle_arc_movement(self, 
                            g_code_line_info: List[Tuple[str, str]], 
                            Movement_Manager: MovementManager) -> None:
        """
        Handles arc movements specified in the G-code line.

        Parameters:
        -----------
        g_code_line_info : List[Tuple[str, str]]
            List of tuples where each tuple contains a command (letter) and a corresponding value.
        Movement_Manager : MovementManager
            An instance of the MovementManager class to manage movements.
        """

        g_code_line_info_index = 0              # Define index for line_info

        relevant_commands = ["X", "Y", "Z", "A", "B", "C", "I", "J", "K", "R"] # relevent commands for linear movement

        # Initialize arc information with current positions
        match self.cnc_status_current_line.active_plane:
            case 17:
                self.cnc_status_current_line.arc_information.I = self.cnc_status_current_line.position_linear_axes.X
                self.cnc_status_current_line.arc_information.J = self.cnc_status_current_line.position_linear_axes.Y
                # K not relevant for this arc movement
            case 18:
                raise Exception(f"G02 and G03 are not available in plane 18")    # TODO
            case 19:
                raise Exception(f"G02 and G03 are not available in plane 19")   # TODO

        radius_given = False    # Variable to store if the radius was given

        # Iterate through line info until all commands are processed
        while g_code_line_info_index < len(g_code_line_info):

            command: str = g_code_line_info[g_code_line_info_index][0]               # Get command
            number_for_command: str = g_code_line_info[g_code_line_info_index][1]    # Get number

            if command in relevant_commands:  # Command is useful for this Method
                
                g_code_line_info.pop(g_code_line_info_index)       # Remove command and number from line_info
                
                # Set the parameter to absolute value
                match command:
                    case "X":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_linear_axes.X = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_linear_axes.X += float(number_for_command)
                    case "Y":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_linear_axes.Y = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_linear_axes.Y += float(number_for_command)
                    case "Z":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_linear_axes.Z = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_linear_axes.Z += float(number_for_command)
                    case "A":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_rotation_axes.A = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_rotation_axes.A += float(number_for_command)
                    case "B":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_rotation_axes.B = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_rotation_axes.B += float(number_for_command)
                    case "C":
                        if self.cnc_status_current_line.absolute_position:
                            self.cnc_status_current_line.position_rotation_axes.C = float(number_for_command)
                        else:
                            self.cnc_status_current_line.position_rotation_axes.C += float(number_for_command)
                    case "I":
                        if not self.cnc_status_current_line.active_plane == 19:
                            if self.cnc_status_current_line.absolute_arc_center:
                                self.cnc_status_current_line.arc_information.I = float(number_for_command)
                            else:
                                self.cnc_status_current_line.arc_information.I +=  float(number_for_command)
                    case "J":
                        if not self.cnc_status_current_line.active_plane == 18:
                            if self.cnc_status_current_line.absolute_arc_center:
                                self.cnc_status_current_line.arc_information.J = float(number_for_command)
                            else:
                                self.cnc_status_current_line.arc_information.J += float(number_for_command)
                    case "K":
                        if not self.cnc_status_current_line.active_plane == 17:
                            if self.cnc_status_current_line.absolute_arc_center:
                                self.cnc_status_current_line.arc_information.K = float(number_for_command)
                            else:
                                self.cnc_status_current_line.arc_information.K += float(number_for_command)
                    case "R":
                        radius_given = True
                        self.cnc_status_current_line.arc_information.radius = float(number_for_command)
            else:                               # Command is not useful for this Method
                g_code_line_info_index += 1         # Iterate info index

        
        if radius_given:
            self.compute_arc_center()       # Compute the arc center with a given radius
        else:
            self.compute_radius()           # Compute the radius with a given arc center

        # Inform movement manager
        Movement_Manager.add_arc_movement(g_code_line_index = self.g_code_line_index,                       
                                          last_line_status = self.cnc_status_last_line, 
                                          current_line_status = self.cnc_status_current_line)

    def handle_g04(self, 
                   g_code_line_info: List[Tuple[str, str]], 
                   Sync_Info_Manager: SyncInfoManager,
                   Movement_Manager: MovementManager) -> None:
        """
        Handles the G04 dwell command in the G-code line.

        Parameters:
        -----------
        g_code_line_info : List[Tuple[str, str]]
            List of tuples where each tuple contains a command (letter) and a corresponding value.
        Pause_Manager : PauseManager
            An instance of the PauseManager class to manage pauses.
        Movement_Manager : MovementManager
            An instance of the MovementManager class to manage movements.
        """

        # Search for the P value, should be the first command in the line_info
        for g_code_line_info_index, info in enumerate(g_code_line_info):

            command: str = info[0]                       # Get the command
            number_for_command: str = info[1]            # Get the number

            P_value_found = False                   # Initialize flag to track if P value is found

            if command == "P":                      # P command found

                dwell_time: float = 1000.0 * float(number_for_command)    # convert to ms

                P_value_found = True                                        # Set flag that P value was found             
                g_code_line_info.pop(g_code_line_info_index)                # Remove command and number from line_info
                Sync_Info_Manager.new_dwell(self.g_code_line_index,             # Inform pause manager
                                        dwell_time)     
                Movement_Manager.add_pause(self.g_code_line_index,          # Inform movement manager
                                           dwell_time)  
                break
                
        # Handle Error that the P value was not found
        if not P_value_found:                             
            raise Exception(f"No P value found in combination with a G04 in line {self.g_code_line_index+1}.")

    def handle_abort(self,
                     Sync_Info_Manager: SyncInfoManager,
                     Movement_Manager: MovementManager) -> None:
        """
        Handles the abort command in the G-code line.

        Parameters:
        -----------
        Sync_Info_Manager : SyncInfoManager
            An instance of the SyncInfoManager class to manage the abort.
        Movement_Manager : MovementManager
            An instance of the MovementManager class to manage movements.
        """

        # Inform pause manager to add a new pause with 0 duration, indicating an immediate pause
        Sync_Info_Manager.new_pause(g_code_line_index = self.g_code_line_index, 
                                    kind_of_pause = 0)
        
        # Inform movement manager to add a pause with -1 duration, indicating an abort
        Movement_Manager.add_pause(g_code_line_index = self.g_code_line_index, 
                                   time = -1)

    def handle_quit(self, 
                    Sync_Info_Manager: SyncInfoManager,
                    Movement_Manager: MovementManager) -> None:
        """
        Handles the quit command in the G-code line.

        Parameters:
        -----------
        Pause_Manager : PauseManager
            An instance of the PauseManager class to manage pauses.
        Movement_Manager : MovementManager
            An instance of the MovementManager class to manage movements.
        """

        # Inform pause manager to add a new pause with a duration of 1, indicating a quit command
        Sync_Info_Manager.new_pause(g_code_line_index = self.g_code_line_index, 
                                    kind_of_pause = 1)

        # Inform movement manager to add a pause with -1 duration, indicating a quit command
        Movement_Manager.add_pause(g_code_line_index = self.g_code_line_index, 
                                   time = -1)
    
    def handle_progabort(self, 
                         Sync_Info_Manager: SyncInfoManager, 
                         Movement_Manager: MovementManager) -> None:
        """
        Handles the program abort command in the G-code line.

        Parameters:
        -----------
        Sync_Info_Manager : SyncInfoManager
            An instance of the PauseManager class to manage the pause.
        Movement_Manager : MovementManager
            An instance of the MovementManager class to manage movements.
        """
        
        # Inform pause manager to add a new pause with a duration of 2, indicating a program abort command
        Sync_Info_Manager.new_pause(g_code_line_index = self.g_code_line_index, 
                                    kind_of_pause = 2)

        # Inform movement manager to add a pause with -1 duration, indicating a program abort command
        Movement_Manager.add_pause(g_code_line_index = self.g_code_line_index, 
                                   time = -1)
    
    def handle_spindle_operation(self, 
                                 spindle_command: str, 
                                 Sync_Info_Manager: SyncInfoManager) -> None:
        """
        Handles spindle operation commands in the G-code line.

        Parameters:
        -----------
        spindle_command : str
            The spindle operation command ("CW", "CCW", or "off").
        Frequency_Manager : FrequencyManager
            An instance of the FrequencyManager class to manage spindle operations.
        """
        
        # Update spindle status based on the command
        if spindle_command == "off":                                        
            self.cnc_status_current_line.spindle_on = False
        else:
            self.cnc_status_current_line.spindle_on = True
            self.cnc_status_current_line.spindle_direction = spindle_command
        
        # Inform frequency manager about the spindle operation
        Sync_Info_Manager.new_Spindle_Operation(g_code_line_index = self.g_code_line_index, 
                                                spindle_command = spindle_command)
    
    def handle_tool_change(self, 
                           g_code_line_info: List[Tuple[str, str]], 
                           CNC_Parameter: CNCParameter,
                           Sync_Info_Manager: SyncInfoManager,
                           Movement_Manager: MovementManager) -> None:
        """
        Handles tool change commands in the G-code line.

        Parameters:
        -----------
        g_code_line_info : List[Tuple[str, str]
            A list containing command and value pairs extracted from the G-code line.
        Tool_Change_Manager : ToolChangeManager
            An instance of the ToolChangeManager class to manage tool change operations.
        Movement_Manager : MovementManager
            An instance of the MovementManager class to manage movements.
        """
        
        T_value_found = False   # Flag to track if T value is found

        # Search for T value in g_code_line_info
        for g_code_line_info_index, info in enumerate(g_code_line_info):                        
            if info[0] == "T": 
                # T value found                      

                tool_number = int(info[1])                      # Get tool number
                g_code_line_info.pop(g_code_line_info_index)    # Remove command and number from g_code_line_info
                T_value_found = True                            # Set T_value_found True
        
        # Case: no T value found
        if not T_value_found:
            raise Exception(f"Tool change was called without T value in line {self.g_code_line_index}")
        
        # Set active tool number
        self.cnc_status_current_line.active_tool = tool_number

        # Inform tool change manager
        Sync_Info_Manager.new_Tool(g_code_line_index = self.g_code_line_index)

        # Inform movement manager
        Movement_Manager.add_tool_change(g_code_line_index = self.g_code_line_index)

        # Update current line
        self.cnc_status_current_line.position_linear_axes = copy.deepcopy(CNC_Parameter.TOOL_CHANGE_POSITION_LINEAR_AXES)

    def handle_cooling_operation(self, 
                                 cooling_command: str, 
                                 Sync_Info_Manager: SyncInfoManager) -> None:
        """
        Handles cooling operation commands in the G-code line.

        Parameters:
        -----------
        cooling_command : str
            The cooling operation command ('on' or 'off').
        Sync_Info_Manager : SyncInfoManager
            An instance of the SyncInfoManager class to manage cooling operations.
        """
        # Handle command
        if cooling_command == "off":
            self.cnc_status_current_line.cooling_on = False
        else:
            self.cnc_status_current_line.cooling_on = True

        # Inform cooling manager
        Sync_Info_Manager.new_cooling_operation(self.g_code_line_index, cooling_command) 
    
    def handle_end_of_program(self, 
                              Sync_Info_Manager: SyncInfoManager, 
                              Movement_Manager: MovementManager) -> None:        
        """
        Handles the end of the G-code program.

        Parameters:
        -----------
        Sync_Info_Manager : SyncInfoManager
            An instance of the SyncInfoManager class to manage frequency changes.
        Movement_Manager : MovementManager
            An instance of the MovementManager class to manage movements.
        """

        # Update line status
        self.cnc_status_current_line.spindle_on = False                         # TODO: not shure if this is needed
        self.cnc_status_current_line.program_end_reached = True

        # Inform frequency manager
        Sync_Info_Manager.new_Spindle_Operation(g_code_line_index = self.g_code_line_index,
                                                spindle_command = "off")
        
        # Inform movement manager
        Movement_Manager.add_end_of_program(self.g_code_line_index)

    def compute_arc_center(self) -> None:
        """
        Computes the center of an arc movement based on the current CNC status.

        Raises:
        -------
        Exception:
            If the active plane is not the XY-plane.

        """

        # Get the movement type, 2: CW, 3: CCW
        movement_type: int = self.cnc_status_current_line.arc_information.direction

        # Get start and end position
        start_position_linear_axes = self.cnc_status_last_line.position_linear_axes.get_as_array()
        end_position_end_position = self.cnc_status_current_line.position_linear_axes.get_as_array()

        # Compute the mid point between start and end position
        mid_point = start_position_linear_axes + (end_position_end_position - start_position_linear_axes) * 0.5
        
        # Get the radius
        radius = self.cnc_status_current_line.arc_information.radius

        # Initialize arc center as array
        arc_center = np.zeros(3)

        match self.cnc_status_current_line.active_plane:
            case 17:    # Active plane is the XY-plane

                # Handle Z value
                Z_position = start_position_linear_axes[2]  # Save Z position
                start_position_linear_axes[2] = 0.0         # Set Z value of start position to 0
                mid_point[2] = 0.0                          # Set Z value of end position to 0

                # Compute vector from start to mid point
                start_2_mid_point = mid_point - start_position_linear_axes
                
                 # Create normal vector from XY-plane
                XY_normal_vector = np.array([0.0, 0.0, 1.0])

                # Get the direction of the location of the arc-center
                if (radius >= 0 and movement_type == 2) or (radius < 0 and movement_type == 3):
                    direction = "right"
                else:
                    direction = "left"

                # Compute direction from mid point to arc center
                mid_2_center = vecfunc.compute_normal_vector(vec1 = start_2_mid_point,  
                                                             vec2 = XY_normal_vector, 
                                                             direction = direction)

                # Compute distance from start to mid point
                len_start_2_mid_point = np.linalg.norm(start_2_mid_point)               
                
                # Compute distance from mid point to center
                len_mid_2_center = math.sqrt(math.pow(radius, 2) - math.pow(len_start_2_mid_point, 2))  

                # Adjust the length of the vector from mid to center
                mid_2_center = mid_2_center * len_mid_2_center      

                # Compute arc center
                arc_center = mid_point + mid_2_center               

                # Set Z value
                arc_center[2] = Z_position                      
            case 18:
                raise Exception(f"G02 and G03 are not available in plane 18")    # TODO
            case 19:
                raise Exception(f"G02 and G03 are only available in plane 19")   # TODO

        # Set arc center
        self.cnc_status_current_line.arc_information.set_arc_center_with_array(arc_center)         

    def compute_radius(self) -> None:
        """
        Computes the radius of the arc based on the current CNC status.

        This method calculates the radius of the arc based on the end position
        and the arc center. It ensures that the active plane is the XY-plane (plane 17)
        before computing the radius.

        Raises:
            Exception: If the active plane is not the XY-plane.

        """

        end_position = self.cnc_status_current_line.position_linear_axes.get_as_array()         # Get end position
        arc_center = self.cnc_status_current_line.arc_information.get_arc_center_as_array()     # Get arc center

        match self.cnc_status_current_line.active_plane:
            case 17:    # Active plane is the XY-plane
                # Handle Z value
                end_position[2] = 0.0
                arc_center[2] = 0.0

                # Compute radius
                radius = np.linalg.norm(end_position - arc_center)                      

                # Set radius
                self.cnc_status_current_line.arc_information.radius = radius
            case 18:
                raise Exception(f"G02 and G03 are not available in plane 18 jet")    # TODO
            case 19:
                raise Exception(f"G02 and G03 are only available in plane 19 jet")   # TODO

# End of class
#####################################################################################################
