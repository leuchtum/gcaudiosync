import copy

from gcaudiosync.gcanalyser.movement import Movement
from gcaudiosync.gcanalyser.cncparameter import CNC_Parameter
import gcaudiosync.gcanalyser.vectorfunctions as vecfunc

from gcaudiosync.gcanalyser.cncstatus import CNC_Status

class Movement_Manager:

    expected_time_total: int        = 0         # Total time
    time_stamps: list               = []        # Timestamps for all movements
    movements: Movement             = []        # Movements
    end_of_program_reached: bool    = False     # Variable for end of program

    # Constructor
    def __init__(self, 
                 CNC_Parameter: CNC_Parameter, 
                 first_line_status: CNC_Status):
        
        self.CNC_Parameter = CNC_Parameter          # Get cnc parameter

        movement = Movement(line_index = -1,        # Create first movement
                            movement = -1, 
                            start_position_linear_axes = first_line_status.position_linear_axes, 
                            end_position_linear_axes = first_line_status.position_linear_axes,
                            start_position_rotation_axes = first_line_status.position_rotation_axes,
                            end_position_rotation_axes = first_line_status.position_rotation_axes, 
                            info_arc = None,
                            feed_rate = 0.0)
        
        first_time = 1.0

        movement.expected_time = first_time         # Time for first movement

        self.time_stamps.append(self.expected_time_total)    # Append time stamp
        self.expected_time_total += first_time               # Update total time 
        self.movements.append(movement)             # Append first movement
        
    #################################################################################################
    # Methods

    # Method for linear movement
    def add_linear_movement(self, 
                            line_index: int, 
                            last_line_status: CNC_Status,
                            current_line_status: CNC_Status):

        # Check end of program
        if self.end_of_program_reached:
            return
        
        # last_movement: Movement = copy.deepcopy(self.movements[-1])
        
        # Create new movement
        new_movement = Movement(line_index = line_index, 
                                movement = current_line_status.active_movement, 
                                start_position_linear_axes = last_line_status.position_linear_axes, 
                                end_position_linear_axes = current_line_status.position_linear_axes,
                                start_position_rotation_axes = last_line_status.position_rotation_axes,
                                end_position_rotation_axes = current_line_status.position_rotation_axes, 
                                info_arc = None,
                                feed_rate = current_line_status.feed_rate)
        
        # Add exact stop if needed
        if current_line_status.exact_stop:
            new_movement.do_exact_stop()

        expected_time = new_movement.expected_time              # Get expected time

        self.movements.append(new_movement)                     # Append movement

        self.time_stamps.append(self.expected_time_total)       # Append time stamp

        self.expected_time_total += expected_time               # Update total time

    # Method for arc movement
    def add_arc_movement(self, 
                         line_index: int, 
                         last_line_status: CNC_Status,
                         current_line_status: CNC_Status):

        # Check end of program
        if self.end_of_program_reached:
            return
        
        # last_movement: Movement = copy.deepcopy(self.movements[-1])
        
        # Create new movement
        new_movement = Movement(line_index = line_index, 
                                movement = current_line_status.active_movement, 
                                start_position_linear_axes = last_line_status.position_linear_axes, 
                                end_position_linear_axes = current_line_status.position_linear_axes,
                                start_position_rotation_axes = last_line_status.position_rotation_axes,
                                end_position_rotation_axes = current_line_status.position_rotation_axes, 
                                info_arc = current_line_status.info_arc,
                                feed_rate = current_line_status.feed_rate)
        
        # Add exact stop if needed
        if current_line_status.exact_stop:
            new_movement.do_exact_stop()

        expected_time = new_movement.expected_time              # Get expected time

        self.movements.append(new_movement)                     # Append movement

        self.time_stamps.append(self.expected_time_total)       # Append time stamp

        self.expected_time_total += expected_time               # Update total time

    # Method for tool change
    def add_tool_change(self, 
                        line_index: int):
        
        # Check end of program
        if self.end_of_program_reached:
            return
        
        last_movement: Movement = copy.deepcopy(self.movements[-1])         # Get last movement

        current_position_linear_axes = last_movement.end_position_linear_axes       # Get current position linear axes
        current_position_rotation_axes = last_movement.end_position_rotation_axes   # Get current position rotation axes

        tool_change_position_linear = self.CNC_Parameter.TOOL_CHANGE_POSITION_LINEAR_AXES   # Get tool change position

        # Create movement to tool
        movement_get_tool = Movement(line_index = line_index, 
                                     movement = 0, 
                                     start_position_linear_axes = current_position_linear_axes, 
                                     end_position_linear_axes = tool_change_position_linear,
                                     start_position_rotation_axes = current_position_rotation_axes,
                                     end_position_rotation_axes = current_position_rotation_axes, 
                                     info_arc = None,
                                     feed_rate = self.CNC_Parameter.F_MAX)
        
        movement_get_tool.do_exact_stop()   # Add exact stop

        expected_time = movement_get_tool.expected_time         # Get expected time

        self.movements.append(movement_get_tool)                # Append movement

        self.time_stamps.append(self.expected_time_total)       # Append time stamp

        self.expected_time_total += expected_time               # Update total time       
        
        self.add_pause(line_index = line_index, time = self.CNC_Parameter.TOOL_CHANGE_TIME) # Add pause for tool change

    # Method for pause
    def add_pause(self, 
                  line_index: int, 
                  time: int):
        
        default_pause_time = 10000                                  # Default time if unknown

        last_movement: Movement = copy.deepcopy(self.movements[-1]) # Get last movement

        # create new movement
        new_movement = Movement(line_index = line_index, 
                                movement = -1, 
                                start_position_linear_axes = last_movement.end_position_linear_axes, 
                                end_position_linear_axes = last_movement.end_position_linear_axes,
                                start_position_rotation_axes = last_movement.end_position_linear_axes,
                                end_position_rotation_axes = last_movement.end_position_rotation_axes, 
                                info_arc = None,
                                feed_rate = 0)
        
        # Check if unknown pause time
        if time == -1:
            time = default_pause_time

        new_movement.expected_time = time                   # Set time
        
        self.time_stamps.append(self.expected_time_total)   # Append time stamp

        self.expected_time_total += time                    # Update expected time total

        self.movements[-1].do_exact_stop()                  # Add exact stop to last movement

        self.movements.append(new_movement)                 # Append movement
    
    # Method for end of program
    def add_end_of_program(self, 
                       line_index: int):
        
        self.end_of_program_reached = True  # Set variable
        self.add_pause(line_index, 1)       # Add final pause

    # Method to get expeted time of one line
    def get_expected_time_of_gcode_line(self, 
                                        line_index: int):

        expected_time: int = 0                                          # Set expected time to 0

        # Iterate backwards through all movements and find thouse who match the line index
        for index in range(len(self.movements))[::-1]:

            if self.movements[index].line_index < line_index:           # All movements found
                break                                                       # Break loop
            elif self.movements[index].line_index == line_index:        # Found matching line index
                expected_time += self.movements[index].expected_time        # Update expected time

        return expected_time

    # Method to get all movement indices of one line
    def get_indices_of_movements_for_gcode_line(self, 
                                                line_index: int):

        indices: list = []                                              # Create empty list

        # Iterate backwards through all movements and find thouse who match the line index
        for movement_index in range(len(self.movements))[::-1]:

            if self.movements[movement_index].line_index < line_index:      # All movements found
                break                                                           # Break loop
            elif self.movements[movement_index].line_index == line_index:   # Matching line index found
                indices.append(movement_index)                                  # Append index

        return indices

    # Method to get a position at a given time
    def get_position_linear(self, 
                            current_time: int):
        
        time_stamp_found = False                            # Variable to check if time stamp was found

        # Iterate through all time stamps
        for index in range(len(self.time_stamps)-1):

            if current_time <= self.time_stamps[index+1]:   # Check if current time is in this time stamp
                time_stamp_found = True                         # Set variable
                break                                           # Break loop
                
        # Excaption handeling
        if not time_stamp_found:
            raise Exception(f"No movement found for this time.")

        time_in_movement = current_time - self.time_stamps[index]                       # Compute the time in this movement

        # Excaption handeling
        if time_in_movement < 0:
            raise Exception(f"Error: Current time is negative.")
        
        current_movement: Movement = self.movements[index]                              # Get current movement

        current_position_linear_axes = current_movement.get_position_linear_axes_in_movement(time_in_movement)  # Get position

        return current_position_linear_axes
    
    # Method to print the info of the movement manager with all movements
    def print_info(self):
        print(f"total_time: {self.expected_time_total}")
        print(f"nof movements: {len(self.movements)}")
        print("")

        for movement_index in range(len(self.movements)):
            print(f"Movement no. {movement_index}")
            print(f"time stamp: {self.time_stamps[movement_index]}")
            self.movements[movement_index].print_info()
            print("")

# End of class
#####################################################################################################
