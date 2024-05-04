import numpy as np
import copy

from gcaudiosync.gcanalyser.movement import Movement
from gcaudiosync.gcanalyser.cncparameter import CNC_Parameter
import gcaudiosync.gcanalyser.vectorfunctions as vecfunc

from gcaudiosync.gcanalyser.cncstatus import CNC_Status

class Movement_Manager:

    # counter = 0

    total_time = 0
    time_stamps = []
    movements: Movement = []

    def __init__(self, 
                 CNC_Parameter: CNC_Parameter, 
                 first_line_status: CNC_Status):
        
        self.CNC_Parameter = CNC_Parameter

        movement = Movement(line_index = -1, 
                            movement = -1, 
                            start_point_linear = first_line_status.position_linear, 
                            end_point_linear = first_line_status.position_linear,
                            start_point_rotation = first_line_status.position_rotation,
                            end_point_rotation = first_line_status.position_rotation, 
                            info_arc=None,
                            feed_rate = 0)
        
        movement.expected_time = 10.0

        self.time_stamps.append(self.total_time)
        self.total_time = 10.0
        self.movements.append(movement)
        

    def add_linear_movement(self, 
                            index: int, 
                            last_line_status: CNC_Status,
                            line_status: CNC_Status):
        
        last_movement: Movement = copy.deepcopy(self.movements[-1])

        new_movement = Movement(line_index = index, 
                                movement = line_status.active_movement, 
                                start_point_linear = last_line_status.position_linear, 
                                end_point_linear = line_status.position_linear,
                                start_point_rotation = last_line_status.position_rotation,
                                end_point_rotation = line_status.position_rotation, 
                                info_arc = None,
                                feed_rate = line_status.feed_rate)
        
        if line_status.exact_stop:
            new_movement.do_exact_stop()

        expected_time = new_movement.expected_time

        self.movements.append(new_movement)
        self.time_stamps.append(self.total_time)
        self.total_time += expected_time

    def add_arc_movement(self, 
                         index: int, 
                         last_line_status: CNC_Status,
                         line_status: CNC_Status):
        
        last_movement: Movement = copy.deepcopy(self.movements[-1])

        new_movement = Movement(line_index = index, 
                                movement = line_status.active_movement, 
                                start_point_linear = last_line_status.position_linear, 
                                end_point_linear = line_status.position_linear,
                                start_point_rotation = last_line_status.position_rotation,
                                end_point_rotation = line_status.position_rotation, 
                                info_arc = line_status.info_arc,
                                feed_rate = line_status.feed_rate)
        
        if line_status.exact_stop:
            new_movement.do_exact_stop()

        expected_time = new_movement.expected_time

        self.movements.append(new_movement)
        self.time_stamps.append(self.total_time)
        self.total_time += expected_time

    def add_tool_change(self, 
                        line_index: int):
        
        last_movement: Movement = copy.deepcopy(self.movements[-1])

        current_position_linear = last_movement.end_point_linear
        current_position_rotation = last_movement.end_point_rotation

        tool_change_position_linear = self.CNC_Parameter.TOOL_CHANGE_POSITION_LINEAR

        movement_get_tool = Movement(line_index = line_index, 
                                     movement = 0, 
                                     start_point_linear = current_position_linear, 
                                     end_point_linear = tool_change_position_linear,
                                     start_point_rotation = current_position_rotation,
                                     end_point_rotation = current_position_rotation, 
                                     info_arc = None,
                                     feed_rate = self.CNC_Parameter.F_MAX)
        movement_get_tool.do_exact_stop()

        expected_time = movement_get_tool.compute_expected_time()

        self.movements.append(movement_get_tool)
        self.time_stamps.append(self.total_time)
        self.total_time += expected_time        
        
        self.add_pause(line_index = line_index, time = self.CNC_Parameter.TOOL_CHANGE_TIME)
        
        movement_back_2_current_position = Movement(line_index = line_index, 
                                                    movement = 0, 
                                                    start_point_linear = tool_change_position_linear, 
                                                    end_point_linear = current_position_linear,
                                                    start_point_rotation = current_position_rotation,
                                                    end_point_rotation = current_position_rotation, 
                                                    info_arc = None,
                                                    feed_rate = self.CNC_Parameter.F_MAX)
        movement_back_2_current_position.do_exact_stop()

        expected_time = movement_back_2_current_position.compute_expected_time()

        self.movements.append(movement_back_2_current_position)
        self.time_stamps.append(self.total_time)
        self.total_time += expected_time

        return 0 # time
    
    def add_pause(self, line_index: int, time: int):

        last_movement:Movement = copy.deepcopy(self.movements[-1])

        movement = Movement(line_index = line_index, 
                            movement = -1, 
                            start_point_linear = last_movement.end_point_linear, 
                            end_point_linear = last_movement.end_point_linear,
                            start_point_rotation = last_movement.end_point_linear,
                            end_point_rotation = last_movement.end_point_rotation, 
                            info_arc = None,
                            feed_rate = 0)
        
        movement.expected_time = time
        
        self.time_stamps.append(self.total_time)
        self.total_time += time

        self.movements[-1].do_exact_stop()

        self.movements.append(movement)

    # TODO
    def update_vectors_linear_of_movements(self):
        pass

    def get_expected_time(self, line_index: int):

        expected_time = 0

        for index in range(len(self.movements))[::-1]:

            if self.movements[index].line_index < line_index:
                break
            elif self.movements[index].line_index == line_index:
                expected_time += self.movements[index].expected_time

        return expected_time

    def get_indices_of_movements(self, line_index: int):

        indices = []

        for index in range(len(self.movements))[::-1]:

            if self.movements[index].line_index < line_index:
                break
            elif self.movements[index].line_index == line_index:
                indices.append(index)

        return indices

    def get_position_linear(self, current_time):
        
        time_stamp_found = False

        for index in range(len(self.time_stamps)-1):
            if current_time <= self.time_stamps[index+1]:
                time_stamp_found = True
                break

        if not time_stamp_found:
            raise Exception("No movement found for this time")

        time_in_movement = current_time - self.time_stamps[index]

        current_movement: Movement = self.movements[index]

        current_position = current_movement.get_position_in_movement(time_in_movement)

        return current_position
    
    def print_info(self):
        print(f"total_time: {self.total_time}")
        print(f"nof movements: {len(self.movements)}")
        print("")

        for index in range(len(self.movements)):
            print(f"Movement no. {index}")
            print(f"time stamp: {self.time_stamps[index]}")
            self.movements[index].print_info()
            print("")