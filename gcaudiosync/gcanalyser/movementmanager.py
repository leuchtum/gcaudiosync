import copy

from gcaudiosync.gcanalyser.movement import Movement
from gcaudiosync.gcanalyser.cncparameter import CNCParameter
import gcaudiosync.gcanalyser.vectorfunctions as vecfunc

from gcaudiosync.gcanalyser.cncstatus import CNCStatus
from gcaudiosync.gcanalyser.toolpathinformation import ToolPathInformation
from gcaudiosync.gcanalyser.linearaxes import LinearAxes
from gcaudiosync.gcanalyser.rotationaxes import RotationAxes
from gcaudiosync.gcanalyser.arcinformation import ArcInformation


class MovementManager:

    start_time : int                = 0         # Time for the start
    total_time: int                 = 0         # Expected total time
    movements: Movement             = []        # Movements
    end_of_program_reached: bool    = False     # Variable for end of program

    # Constructor
    def __init__(self, 
                 CNC_Parameter: CNCParameter, 
                 first_line_status: CNCStatus):
        
        self.CNC_Parameter = CNC_Parameter          # Get cnc parameter

        first_movement = Movement(line_index = -1,        # Create first movement
                                  movement_type = -1, 
                                  start_position_linear_axes    = first_line_status.position_linear_axes, 
                                  end_position_linear_axes      = first_line_status.position_linear_axes,
                                  start_position_rotation_axes  = first_line_status.position_rotation_axes,
                                  end_position_rotation_axes    = first_line_status.position_rotation_axes, 
                                  arc_information = None,
                                  feed_rate = 0.0)
        
        first_movement.time = 0                                 # Time for first movement

        self.movements.append(first_movement)                   # Append first movement
        
    #################################################################################################
    # Methods

    # Method for linear movement
    def add_linear_movement(self, 
                            line_index: int, 
                            last_line_status: CNCStatus,
                            current_line_status: CNCStatus):

        # Check end of program
        if self.end_of_program_reached:
            return
                
        # Create new movement
        new_movement = Movement(line_index = line_index, 
                                movement_type = current_line_status.active_movement_type, 
                                start_position_linear_axes = last_line_status.position_linear_axes, 
                                end_position_linear_axes = current_line_status.position_linear_axes,
                                start_position_rotation_axes = last_line_status.position_rotation_axes,
                                end_position_rotation_axes = current_line_status.position_rotation_axes, 
                                arc_information = None,
                                feed_rate = current_line_status.feed_rate)
        
        # Add exact stop if needed
        if current_line_status.exact_stop:
            new_movement.do_exact_stop()

        self.movements.append(new_movement)                     # Append movement

    # Method for arc movement
    def add_arc_movement(self, 
                         line_index: int, 
                         last_line_status: CNCStatus,
                         current_line_status: CNCStatus):

        # Check end of program
        if self.end_of_program_reached:
            return
                
        # Create new movement
        new_movement = Movement(line_index = line_index, 
                                movement_type = current_line_status.active_movement_type,
                                start_position_linear_axes = last_line_status.position_linear_axes, 
                                end_position_linear_axes = current_line_status.position_linear_axes,
                                start_position_rotation_axes = last_line_status.position_rotation_axes,
                                end_position_rotation_axes = current_line_status.position_rotation_axes, 
                                arc_information = current_line_status.arc_information,
                                feed_rate = current_line_status.feed_rate)
        
        # Add exact stop if needed
        if current_line_status.exact_stop:
            new_movement.do_exact_stop()

        self.movements.append(new_movement)                     # Append movement

    # Method for tool change
    def add_tool_change(self, 
                        line_index: int):
        
        # Check end of program
        if self.end_of_program_reached:
            return
        
        last_movement: Movement = copy.deepcopy(self.movements[-1])         # Get last movement

        current_position_linear_axes = last_movement.end_position_linear_axes.get_as_array()        # Get current position linear axes
        current_position_rotation_axes = last_movement.end_position_rotation_axes.get_as_array()    # Get current position rotation axes

        tool_change_position_linear = self.CNC_Parameter.TOOL_CHANGE_POSITION_LINEAR_AXES.get_as_array()    # Get tool change position

        # Create movement to tool
        movement_get_tool = Movement(line_index = line_index, 
                                     movement_type = 0, 
                                     start_position_linear_axes = current_position_linear_axes, 
                                     end_position_linear_axes = tool_change_position_linear,
                                     start_position_rotation_axes = current_position_rotation_axes,
                                     end_position_rotation_axes = current_position_rotation_axes, 
                                     arc_information = None,
                                     feed_rate = self.CNC_Parameter.F_MAX)
        
        movement_get_tool.do_exact_stop()   # Add exact stop

        self.movements.append(movement_get_tool)                # Append movement
        
        self.add_pause(line_index = line_index, 
                       time = self.CNC_Parameter.TOOL_CHANGE_TIME) # Add pause for tool change

    # Method for pause
    def add_pause(self, 
                  line_index: int, 
                  time: int):
        
        default_pause_time = 10000                                  # Default time if unknown

        last_movement: Movement = copy.deepcopy(self.movements[-1]) # Get last movement

        # create new movement
        new_movement = Movement(line_index = line_index, 
                                movement_type = -1, 
                                start_position_linear_axes = copy.deepcopy(last_movement.end_position_linear_axes), 
                                end_position_linear_axes = copy.deepcopy(last_movement.end_position_linear_axes),
                                start_position_rotation_axes = copy.deepcopy(last_movement.end_position_linear_axes),
                                end_position_rotation_axes = copy.deepcopy(last_movement.end_position_rotation_axes), 
                                arc_information = None,
                                feed_rate = 0)
        
        # Check if unknown pause time
        if time == -1:
            time = default_pause_time

        new_movement.time = time                   # Set time
        
        self.movements[-1].do_exact_stop()                  # Add exact stop to last movement

        self.movements.append(new_movement)                 # Append movement
    
    # Method for end of program
    def add_end_of_program(self, 
                           line_index: int):
        
        self.end_of_program_reached = True  # Set variable
        self.add_pause(line_index, 0)       # Add final pause

    # Method to get expected time of one line
    def get_expected_time_of_gcode_line(self, 
                                        line_index: int):

        expected_time: int = 0                                          # Set expected time to 0

        # Iterate backwards through all movements and find thouse who match the line index
        for index in range(len(self.movements))[::-1]:

            if self.movements[index].line_index < line_index:           # All movements found
                break                                                       # Break loop
            elif self.movements[index].line_index == line_index:        # Found matching line index
                expected_time += self.movements[index].time        # Update expected time

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

    def get_tool_path_information(self, 
                                  current_time: int):

        tool_path_information = ToolPathInformation()

        time_stamp_found = False                            # Variable to check if time stamp was found

        # Iterate through all time stamps
        for movement in self.movements:
            
            movement_start_time = movement.start_time
            movement_end_time = movement_start_time + movement.time

            if current_time >= movement_start_time and current_time < movement_end_time:  # Check if current time is in this time stamp
                time_stamp_found = True                         # Set variable
                break                                           # Break loop
                
        # Excaption handeling
        if not time_stamp_found:
            raise Exception(f"No movement found for this time.")
        
        time_in_movement = current_time - movement_start_time   # Compute the time in this movement

        # Excaption handeling
        if time_in_movement < 0:
            raise Exception(f"Error: Current time is negative.")
        
        current__line_index = movement.line_index
        tool_path_information.line_index = current__line_index

        current_position_linear_axes = movement.get_position_linear_axes_in_movement(time_in_movement)  # Get position
        tool_path_information.position_linear_axes = current_position_linear_axes

        tool_path_information.movement = movement.movement_type

        return tool_path_information
 
    # Method to print the info of the movement manager with all movements
    def print_info(self):
        print(f"total_time: {self.total_time}")
        print(f"nof movements: {len(self.movements)}")
        print("")

        for movement_index in range(len(self.movements)):
            print(f"Movement no. {movement_index}")
            print(f"time stamp: {self.movements[movement_index].start_time}")
            self.movements[movement_index].print_info()
            print("")

    # TODO: Dwell times will be adjusted too. this has to change!
    def all_lines_analysed(self):

        # Todo: compute all the start and end vectors

        time: int = 0

        for movement in self.movements:
            movement.compute_expected_time()
            movement.start_time = time
            time += movement.time

        self.total_time = time

    def set_start_time_and_total_time(self, 
                                      new_start_time: int,
                                      new_total_time: int,      # time between start time end time
                                      ): 
        
        if self.total_time <= 0:
            raise Exception("Something went wrong: expected total time <= 0")

        offset = new_start_time
        factor: float = float(new_total_time) / self.total_time

        self.start_time = new_start_time
        self.total_time = new_total_time

        for movement in self.movements:
            movement.adjust_start_and_total_time(offset, factor)
        
        self.movements[0].start_time = 0
        self.movements[0].time = offset

        self.movements[0].is_adjustable = False
        self.movements[-1].is_adjustable = False

    def adjust_start_time_of_g_code_line(self,
                                         line_index,
                                         new_start_time):
        
        for movement_index, movement in enumerate(self.movements):
            if movement.line_index >= line_index:
                important_movement_index = movement_index
                break

        if self.movements[important_movement_index].start_time_is_adjustable:
            self.movements[important_movement_index].start_time_is_adjustable = False
        else:
            pass    # should we do something in this case?

        non_adjustable_index_before = 0
        for movement_index in range(important_movement_index)[::-1]:
            if not self.movements[movement_index].start_time_is_adjustable:
                non_adjustable_index_before = movement_index
                break
        
        non_adjustable_index_after = len(self.movements) - 1
        for movement_index in range(important_movement_index + 1, len(self.movements)):
            if not self.movements[movement_index].start_time_is_adjustable:
                non_adjustable_index_after = movement_index

        non_adjustable_movement_before = self.movements[non_adjustable_index_before]
        non_adjustable_movement_after = self.movements[non_adjustable_index_after]

        time_before_movement = movement.start_time - non_adjustable_movement_before.start_time
        time_after_movement = non_adjustable_movement_after.start_time - time_before_movement

        # TODO
        time_before_movement = movement.start_time - self.start_time
        time_after_movement = self.total_time - time_before_movement

        offset = self.movements[0].time

        factor_before: float = (new_start_time - self.start_time) / time_before_movement
        factor_after: float = (self.total_time + offset - new_start_time) / time_after_movement

        for index in range(1, important_movement_index-1):
            new_movement_start_time: float= self.movements[index-1].start_time + self.movements[index-1].time
            new_movement_time: float = self.movements[index].time * factor_before
            self.movements[index].start_time = new_movement_start_time
            self.movements[index].time = new_movement_time

        new_movement_start_time= self.movements[important_movement_index-2].start_time + self.movements[important_movement_index-2].time
        new_movement_time = new_start_time - new_movement_start_time
        self.movements[important_movement_index-1].start_time = new_movement_start_time
        self.movements[important_movement_index-1].time = new_movement_time

        new_movement_time = self.movements[important_movement_index].time * factor_after
        self.movements[important_movement_index].start_time = new_start_time
        self.movements[important_movement_index].time = new_movement_time

        for index in range(important_movement_index+1, len(self.movements)-1):
            new_movement_start_time= self.movements[index-1].start_time + self.movements[index-1].time
            new_movement_time = self.movements[index].time * factor_after
            self.movements[index].start_time = new_movement_start_time
            self.movements[index].time = new_movement_time

        new_movement_start_time = self.movements[-2].start_time + self.movements[-2].time
        new_movement_time = self.total_time + offset - new_movement_start_time
        self.movements[-1].start_time = new_movement_start_time
        self.movements[-1].time = new_movement_time

    def adjust_end_time_of_g_code_line(self,
                                       line_index,
                                       new_end_time):
        self.adjust_start_time_of_g_code_line(line_index + 1,
                                              new_end_time)


    def get_time_stamps(self):
        time_stamps = []

        g_code_line_index = 0
        g_code_line_time_stamp = 0

        for index, movement in enumerate(self.movements):
            if index > 0:
                new_g_code_line = movement.line_index
                if new_g_code_line != g_code_line_index:
                    g_code_line_index = new_g_code_line
                    g_code_line_time_stamp = movement.start_time
                    time_stamps.append([g_code_line_index, g_code_line_time_stamp])

        return time_stamps

# End of class
#####################################################################################################
