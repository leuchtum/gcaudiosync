import copy
import numpy as np

from typing import List, Tuple

import gcaudiosync.gcanalyser.vectorfunctions as vecfunc

from gcaudiosync.gcanalyser.arcinformation import ArcInformation
from gcaudiosync.gcanalyser.cncparameter import CNCParameter
from gcaudiosync.gcanalyser.cncstatus import CNCStatus
from gcaudiosync.gcanalyser.linearaxes import LinearAxes
from gcaudiosync.gcanalyser.movement import Movement
from gcaudiosync.gcanalyser.rotationaxes import RotationAxes
from gcaudiosync.gcanalyser.toolpathinformation import ToolPathInformation

class MovementManager:
    """
    A class to manage movements in CNC machining.

    Attributes:
    -----------
    start_time : int
        Time for the start.
    total_time : int
        Expected total time.
    movements : List[Movement]
        List of movements.
    end_of_program_reached : bool
        Indicates if the end of the program has been reached.
    CNC_Parameter : CNCParameter
        CNC parameter instance.
    """

    # Constructor
    def __init__(self, 
                 CNC_Parameter: CNCParameter):
        """
        A class to manage movements in CNC machining.

        Attributes:
        -----------
        start_time : int
            Time for the start.
        total_time : int
            Expected total time.
        movements : List[Movement]
            List of movements.
        end_of_program_reached : bool
            Indicates if the end of the program has been reached.
        CNC_Parameter : CNCParameter
            CNC parameter instance.
        """

        self.start_time : float             = 0.0       # Time for the start
        self.total_duration: float          = 0.0       # Expected total time
        self.movements: List[Movement]      = []        # Movements
        self.end_of_program_reached: bool   = False     # Variable for end of program
        
        self.CNC_Parameter: CNCParameter    = CNC_Parameter              # Get cnc parameter

        self.movement_dynamic_is_ok: bool   = False

        # Get max acceleration and deceleration
        self.max_acceleration: np.array     = self.CNC_Parameter.get_acceleration_as_array()
        self.max_deceleration: np.array     = self.CNC_Parameter.get_deceleration_as_array()

        # Create the initial CNC_Status object for the initialization of the MovementManager object
        first_line_status: CNCStatus = CNCStatus(start_position = True, 
                                                 CNC_Parameter = self.CNC_Parameter)

        # Create first movement
        first_movement: Movement = Movement(g_code_line_index = -1,        
                                            movement_type = -1, 
                                            start_position_linear_axes    = first_line_status.position_linear_axes, 
                                            end_position_linear_axes      = first_line_status.position_linear_axes,
                                            start_position_rotation_axes  = first_line_status.position_rotation_axes,
                                            end_position_rotation_axes    = first_line_status.position_rotation_axes, 
                                            arc_information = None,
                                            feed_rate = 0.0,
                                            active_plane = 17,
                                            CNC_Parameter = self.CNC_Parameter)
        
        # Time for first movement and set flags
        first_movement.duration = 0.0
        first_movement.time_is_adjustable = False
        first_movement.start_time_is_adjustable = False          

        # Append first movement
        self.movements.append(first_movement)                   
        
    #################################################################################################
    # Methods

    def add_linear_movement(self, 
                            g_code_line_index: int, 
                            last_line_status: CNCStatus,
                            current_line_status: CNCStatus) -> None:
        """
        Adds a linear movement to the list of movements.

        Parameters:
        -----------
        line_index : int
            The line index of the G-code corresponding to this movement.
        last_line_status : CNCStatus
            Status of the CNC at the previous line.
        current_line_status : CNCStatus
            Status of the CNC at the current line.
        """

        # Check end of program
        if self.end_of_program_reached:
            return
                
        # Create new movement
        new_movement: Movement = Movement(g_code_line_index = g_code_line_index, 
                                          movement_type = current_line_status.active_movement_type, 
                                          start_position_linear_axes = last_line_status.position_linear_axes, 
                                          end_position_linear_axes = current_line_status.position_linear_axes,
                                          start_position_rotation_axes = last_line_status.position_rotation_axes,
                                          end_position_rotation_axes = current_line_status.position_rotation_axes, 
                                          arc_information = None,
                                          feed_rate = current_line_status.feed_rate,
                                          active_plane = current_line_status.active_plane,
                                          CNC_Parameter = self.CNC_Parameter)
        
        # Add exact stop if needed
        if current_line_status.exact_stop:
            new_movement.do_exact_stop()

        # Append movement
        self.movements.append(new_movement)                     

    def add_arc_movement(self, 
                         g_code_line_index: int, 
                         last_line_status: CNCStatus,
                         current_line_status: CNCStatus) -> None:
        """
        Adds an arc movement to the list of movements.

        Parameters:
        -----------
        line_index : int
            The line index of the G-code corresponding to this movement.
        last_line_status : CNCStatus
            Status of the CNC at the previous line.
        current_line_status : CNCStatus
            Status of the CNC at the current line.
        """

        # Check end of program
        if self.end_of_program_reached:
            return
                
        # Create new movement
        new_movement: Movement = Movement(g_code_line_index = g_code_line_index, 
                                          movement_type = current_line_status.active_movement_type,
                                          start_position_linear_axes = last_line_status.position_linear_axes, 
                                          end_position_linear_axes = current_line_status.position_linear_axes,
                                          start_position_rotation_axes = last_line_status.position_rotation_axes,
                                          end_position_rotation_axes = current_line_status.position_rotation_axes, 
                                          arc_information = current_line_status.arc_information,
                                          feed_rate = current_line_status.feed_rate,
                                          active_plane = current_line_status.active_plane,
                                          CNC_Parameter = self.CNC_Parameter)
        
        # Add exact stop if needed
        if current_line_status.exact_stop:
            new_movement.do_exact_stop()

        # Append movement
        self.movements.append(new_movement)                     

    def add_tool_change(self, 
                        g_code_line_index: int) -> None:
        """
        Adds a tool change movement to the list of movements.

        Parameters:
        -----------
        g_code_line_index : int
            The line index of the G-code corresponding to this tool change.
        """

        # Check end of program
        if self.end_of_program_reached:
            return
        
        # Get last movement
        last_movement: Movement = copy.deepcopy(self.movements[-1])         

        # Get current positions
        current_position_linear_axes = last_movement.end_position_linear_axes
        current_position_rotation_axes = last_movement.end_position_rotation_axes

        # Get tool change position
        tool_change_position_linear = self.CNC_Parameter.TOOL_CHANGE_POSITION_LINEAR_AXES

        # Create movement to tool
        movement_get_tool: Movement = Movement(g_code_line_index = g_code_line_index, 
                                               movement_type = 0, 
                                               start_position_linear_axes = current_position_linear_axes, 
                                               end_position_linear_axes = tool_change_position_linear,
                                               start_position_rotation_axes = current_position_rotation_axes,
                                               end_position_rotation_axes = current_position_rotation_axes, 
                                               arc_information = None,
                                               feed_rate = self.CNC_Parameter.F_MAX / 60000.0,
                                               active_plane = 17,
                                               CNC_Parameter = self.CNC_Parameter)
        
        # Add exact stop
        movement_get_tool.do_exact_stop()   

        # Append movement
        self.movements.append(movement_get_tool)                
        
        # Add pause for tool change
        self.add_pause(g_code_line_index = g_code_line_index, 
                       time = self.CNC_Parameter.TOOL_CHANGE_TIME) 

    def add_pause(self, 
                  g_code_line_index: int, 
                  time: float) -> None:
        """
        Adds a pause movement to the list of movements.

        Parameters:
        -----------
        g_code_line_index : int
            The line index of the G-code corresponding to this pause.
        time : int
            The duration of the pause.
        """

        # Default time if unknown
        default_pause_time: float = self.CNC_Parameter.DEFAULT_PAUSE_TIME                                  

        # Get last movement
        last_movement: Movement = copy.deepcopy(self.movements[-1]) 

        # create new movement
        new_movement: Movement = Movement(g_code_line_index = g_code_line_index, 
                                          movement_type = -1, 
                                          start_position_linear_axes = last_movement.end_position_linear_axes, 
                                          end_position_linear_axes = last_movement.end_position_linear_axes,
                                          start_position_rotation_axes = last_movement.end_position_linear_axes,
                                          end_position_rotation_axes = last_movement.end_position_rotation_axes, 
                                          arc_information = None,
                                          feed_rate = 0,
                                          active_plane = 17,
                                          CNC_Parameter = self.CNC_Parameter)
        
        # Check if unknown pause time
        if time == -1:
            time = default_pause_time

        # Set time and set flags
        new_movement.duration = time      
        new_movement.time_is_adjustable = False             
        
        # Add exact stop to last movement
        self.movements[-1].do_exact_stop()                  

        # Append movement
        self.movements.append(new_movement)                 
    
    def add_end_of_program(self, 
                           g_code_line_index: int) -> None:
        """
        Marks the end of the program and adds a final pause.

        Parameters:
        -----------
        line_index : int
            The line index of the G-code corresponding to the end of the program.
        """
        self.end_of_program_reached = True  # Set variable
        # Add final pause
        self.add_pause(g_code_line_index = g_code_line_index, 
                       time = 0)       
        
        # Set flags of last movement
        self.movements[-1].start_time_is_adjustable = False

    def get_expected_time_of_gcode_line(self, 
                                        g_code_line_index: int) -> float:
        """
        Computes the expected time for the given line index in the G-code.

        Parameters:
        -----------
        line_index : int
            The line index of the G-code for which the expected time is to be computed.

        Returns:
        --------
        float
            The expected time in milliseconds for the given line index.
        """

        # Set expected time to 0
        expected_time: float = 0.0                                      

        # Iterate backwards through all movements and find thouse who match the line index
        for index in range(len(self.movements))[::-1]:

            if self.movements[index].line_index < g_code_line_index:       # All movements found
                break                                                   # Exit loop
            elif self.movements[index].line_index == g_code_line_index:    # Found matching line index
                expected_time += self.movements[index].duration             # Update expected time

        return expected_time

    def get_indices_of_movements_for_gcode_line(self, 
                                                g_code_line_index: int,
                                                ) -> List[int]:
        """
        Retrieves the indices of all movements corresponding to a given line index in the G-code.

        Parameters:
        -----------
        line_index : int
            The line index of the G-code for which movement indices are to be retrieved.

        Returns:
        --------
        List[int]
            A list containing the indices of all movements corresponding to the given line index.
        """

        indices: List[int] = []                                              # Create empty list

        # Iterate backwards through all movements and find thouse who match the line index
        for movement_index in range(len(self.movements))[::-1]:

            if self.movements[movement_index].g_code_line_index < g_code_line_index:      # All movements found
                break                                                           # Break loop
            elif self.movements[movement_index].g_code_line_index == g_code_line_index:   # Matching line index found
                indices.append(movement_index)                                  # Append index

        return indices

    def get_tool_path_information(self, 
                                  current_time: float,
                                  ) -> ToolPathInformation:
        """
        Retrieves tool path information at a specific time.

        Parameters:
        -----------
        current_time : float
            The current time for which tool path information is to be retrieved.

        Returns:
        --------
        ToolPathInformation
            Object containing information about the tool path at the specified time.
        """

        # Initialize ToolPathInformation object
        Tool_Path_Information = ToolPathInformation()

        # Flag to check if time stamp was found
        time_stamp_found = False                            

        # Iterate through all time stamps
        for movement in self.movements:
            
            # Get the start and end time of the movement
            movement_start_time = movement.start_time
            movement_end_time = movement_start_time + movement.duration

            # Check if current time is in this time stamp
            if current_time >= movement_start_time and current_time < movement_end_time:  
                time_stamp_found = True     # Set Flag
                break                       # Break loop
                
        # Raise exception if no movement is found for the current time
        if not time_stamp_found:
            raise Exception(f"No movement found for this time.")
        
        # Compute the time in this movement
        time_in_movement = current_time - movement_start_time   

        # Raise exception if the computed time within the movement is negative
        if time_in_movement < 0:
            raise Exception(f"Error: Current time is negative.")
        
        # Get the current line index
        Tool_Path_Information.g_code_line_index = movement.g_code_line_index

        # Get the positions
        Tool_Path_Information.position_linear_axes = movement.get_position_linear_axes_in_movement_as_array(time_in_movement)  # Get position

        # Get the movement type
        Tool_Path_Information.movement_type = movement.movement_type

        return Tool_Path_Information
 
    def print_info(self) -> None:
        """
        Prints information about the MovementManager.

        This method prints the total time, the number of movements, and detailed information
        about each movement in the MovementManager instance.
        """
        print(f"total_time: {self.total_duration} ms")
        print(f"# movements: {len(self.movements)}")
        print("")

        for movement_index in range(len(self.movements)):
            print(f"Movement index {movement_index}")
            print(f"time stamp: {self.movements[movement_index].start_time} ms")
            self.movements[movement_index].print_info()
            print("")

    # TODO: comment
    def all_lines_analysed(self) -> None:
        
        break_if_dynamic_status_nok = True

        max_iterations = 10
        iterations = 0

        while not self.movement_dynamic_is_ok and iterations <= max_iterations:
            
            if iterations == max_iterations:
                break_if_dynamic_status_nok = False

            self.copmpute_start_and_end_vectors()
            self.compute_durations_and_times(break_if_dynamic_status_nok = break_if_dynamic_status_nok)
            iterations += 1

    # TODO: comment
    def copmpute_start_and_end_vectors(self) -> None:
                
        # Iterate through all movements and compute the start and end vectors
        for movement_index in range(len(self.movements)-1):

            start_and_end_vector = np.zeros(3)

            # Get old start and end vector
            end_vector_linear_axes_current_movement = copy.copy(self.movements[movement_index].end_vector_linear_axes)
            start_vector_linear_axes_next_movement = copy.copy(self.movements[movement_index+1].start_vector_linear_axes)

            # Compute start and end vector
            if vecfunc.same_direction(end_vector_linear_axes_current_movement,
                                      start_vector_linear_axes_next_movement):
                factor = vecfunc.get_factor(end_vector_linear_axes_current_movement,
                                            start_vector_linear_axes_next_movement)
                if factor >= 1:
                    start_and_end_vector = start_vector_linear_axes_next_movement
                elif factor > 0:
                    start_and_end_vector = end_vector_linear_axes_current_movement
                else: 
                    pass
            else:
                pass
            
            # Set start and end vector
            self.movements[movement_index].end_vector_linear_axes = copy.copy(start_and_end_vector)
            self.movements[movement_index+1].start_vector_linear_axes = copy.copy(start_and_end_vector)

    def compute_durations_and_times(self, 
                                    break_if_dynamic_status_nok: bool) -> None:

        total_duration: float = 0.0

        # Iterate through all movements and compute the start and end vectors
        for movement_index in range(len(self.movements)-1):

            self.movements[movement_index].compute_expected_time()
            self.movements[movement_index].start_time = total_duration
            total_duration += self.movements[movement_index].duration

            if not self.movements[movement_index].dynamic_is_ok:

                self.movement_dynamic_is_ok = False

                if break_if_dynamic_status_nok:
                    return

        self.total_duration = total_duration

    def set_start_time_and_total_time(self, 
                                      new_start_time: float,
                                      new_total_time: float) -> int: 
        """
        Adjusts the start time and total time for the movements, ensuring constraints are met.

        Parameters:
        -----------
        new_start_time : float
            The new start time for the movements.
        new_total_time : float
            The new total duration between the start and end times, not the end time itself.

        Returns:
        --------
        int
            Status code indicating the outcome:
            0 - Success
            1 - New total time is zero or less
            2 - New total time is too short
        """

        if self.total_duration <= 0:
            return 1    # New total time is 0 or less
            raise Exception(f"Something went wrong: expected total time <= 0")  # Just in case someone wants to add exception handling

        # Get nonadjustable and adjustable time
        nonadjustable_time: float = 0
        old_adjustable_time: float = 0

        for movement in self.movements:
            if movement.time_is_adjustable:
                old_adjustable_time += movement.duration

        nonadjustable_time = self.total_duration - old_adjustable_time
        new_adjustable_time = new_total_time - nonadjustable_time

        # Error case
        if new_adjustable_time <= 0:
            return 2    # New total time is too short
            raise Exception(f"Something went wrong: new total time is too short")  # Just in case someone wants to add exception handling
        
        # Compute time-factor for nonadjustable times
        factor_for_adjustable_time: float = new_adjustable_time / old_adjustable_time

        # Set time for initialization movement
        self.movements[0].start_time = 0.0          # For savety
        self.movements[0].duration = new_start_time

        # Iterate through all movements and adjust start time and time
        for movement_index in range(1, len(self.movements)):
            
            # Set start time
            self.movements[movement_index].start_time = self.movements[movement_index-1].start_time + self.movements[movement_index-1].duration

            # Adjust time if possible
            if self.movements[movement_index].time_is_adjustable:
                self.movements[movement_index].duration *= factor_for_adjustable_time

        # Save times
        self.start_time = new_start_time
        self.total_duration = new_total_time
        
        return 0    # Everything is fine
    
    def adjust_start_time_of_g_code_line(self,
                                         g_code_line_index: int,
                                         new_start_time: float) -> int:
        """
        Adjusts the start time of a specific G-code line.

        Parameters:
        -----------
        g_code_line_index : int
            The index of the G-code line to be adjusted.
        new_start_time : float
            The new start time for the specified G-code line.

        Returns:
        --------
        int
            Status code indicating the outcome:
            0 - Success
            1 - No movement with the specified index found
            2 - New total adjustable time is too short
        """
         
        # Get index of important movement in this g_code_line and Error handling
        important_movement_index: int = 0
        for movement_index, movement in enumerate(self.movements):
            if movement.g_code_line_index >= g_code_line_index:
                important_movement_index = movement_index
                break
        if important_movement_index == 0:
            return 1    # no movement with this index found
            raise Exception(f"Something went wrong: no movement with this index")   # Just in case someone wants to add exception handling
                
        # Get index of previous movement with nonadjustable start time
        previous_important_movement_index: int = 0
        for movement_index in range(important_movement_index)[::-1]:
            if not self.movements[movement_index].start_time_is_adjustable:
                previous_important_movement_index = movement_index
                break
        
        # Get index of next movement with nonadjustable start time
        next_important_movement_index: int = len(self.movements)
        for movement_index in range(important_movement_index+1, len(self.movements)):
            if not self.movements[movement_index].start_time_is_adjustable:
                next_important_movement_index = movement_index
                break

        # Get important times before the important movement
        old_total_time_before: float = self.movements[important_movement_index].start_time - self.movements[previous_important_movement_index].start_time
        new_total_time_before: float = new_start_time - self.movements[previous_important_movement_index].start_time
        nonadjustable_time_before: float = 0
        old_adjustable_time_before: float = 0

        for movement_index in range(previous_important_movement_index, important_movement_index):
            if not self.movements[movement_index].time_is_adjustable:
                nonadjustable_time_before += self.movements[movement_index].duration

        old_adjustable_time_before = old_total_time_before - nonadjustable_time_before
        new_adjustable_time_before = new_total_time_before - nonadjustable_time_before

        # Get important times after the important movement
        old_total_time_after: float = self.movements[next_important_movement_index].start_time - self.movements[important_movement_index].start_time
        new_total_time_after: float = self.movements[next_important_movement_index].start_time - new_start_time
        nonadjustable_time_after: float = 0
        old_adjustable_time_after: float = 0

        for movement_index in range(important_movement_index, next_important_movement_index):
            if not self.movements[movement_index].time_is_adjustable:
                nonadjustable_time_after += self.movements[movement_index].duration

        old_adjustable_time_after = old_total_time_after - nonadjustable_time_after
        new_adjustable_time_after = new_total_time_after - nonadjustable_time_after

        # Error handeling
        if new_adjustable_time_before <= 0 or new_adjustable_time_after <= 0:
            return 2    # New total adjustable time is too short
            raise Exception(f"Something went wrong: new total adjustable time is too short")    # Just in case someone wants to add exception handling
        
        # Adjust all the times and start times before the important movement
        factor_for_previous_adjustable_time: float = new_adjustable_time_before / old_adjustable_time_before
        for movement_index in range(previous_important_movement_index, important_movement_index):
            
            # Adjust time if possible
            if self.movements[movement_index].time_is_adjustable:
                self.movements[movement_index].duration *= factor_for_previous_adjustable_time

            # Set start time of next movement
            self.movements[movement_index+1].start_time = self.movements[movement_index].start_time + self.movements[movement_index].duration

        # Adjust all the times and start times after the important movement
        factor_for_after_adjustable_time: float = new_adjustable_time_after / old_adjustable_time_after
        for movement_index in range(important_movement_index, next_important_movement_index):

            # Adjust time if possible
            if self.movements[movement_index].time_is_adjustable:
                self.movements[movement_index].duration *= factor_for_after_adjustable_time

            # Set start time of next movement
            if movement_index != next_important_movement_index-1:
                self.movements[movement_index+1].start_time = self.movements[movement_index].start_time + self.movements[movement_index].duration

        # Set flag of important movement
        self.movements[important_movement_index].start_time_is_adjustable = False

        return 0 # Everything went fine

    def adjust_end_time_of_g_code_line(self,
                                       g_code_line_index: int,
                                       new_end_time: float):
        """
        Adjusts the end time of a specific G-code line.

        Parameters:
        -----------
        g_code_line_index : int
            The index of the G-code line to be adjusted.
        new_start_time : float
            The new start time for the specified G-code line.

        Returns:
        --------
        int
            Status code indicating the outcome:
            0 - Success
            1 - No movement with the specified index found
            2 - New total adjustable time is too short
        """

        return_value = self.adjust_start_time_of_g_code_line(g_code_line_index + 1,
                                                             new_end_time)

        return return_value

    def get_time_stamps(self) -> List[Tuple[int, float]]:
        """
        Retrieves time stamps for each G-code line.

        This method iterates through all movements and identifies the time stamps for each G-code line.
        A time stamp consists of the G-code line index and its corresponding time stamp.
        
        Returns:
        --------
        List: A list of tuples, where each tuple contains the G-code line index and its time stamp.        """
        time_stamps: List[Tuple[int, float]] = [[0, 0.0]]

        g_code_line_index: int = 0
        g_code_line_time_stamp: float = 0

        # Get all the time stamps   
        for movement_index in range(1, len(self.movements)):

            g_code_line_index_for_this_movement = self.movements[movement_index].g_code_line_index

            if g_code_line_index_for_this_movement != g_code_line_index:
                g_code_line_index = g_code_line_index_for_this_movement
                g_code_line_time_stamp = self.movements[movement_index].start_time
                time_stamps.append([g_code_line_index, g_code_line_time_stamp])

        return time_stamps

# End of class
#####################################################################################################
