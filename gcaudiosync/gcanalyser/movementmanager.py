import numpy as np

from gcaudiosync.gcanalyser.movement import Movement
from gcaudiosync.gcanalyser.cncstatus import CNC_Status

class Movement_Manager:

    counter = 0

    def __init__(self):
        pass

    def add_linear_movement(self, 
                            index: int, 
                            last_line_status: CNC_Status, 
                            line_status: CNC_Status):
        self.counter += 1
        print("Movement_Manager call no. " +  str(self.counter) + ": linear movement in line " + str(index))

    def add_arc_movement(self, 
                         index: int, 
                         last_line_status: CNC_Status, 
                         line_status: CNC_Status):
        self.counter += 1
        print("Movement_Manager call no. " +  str(self.counter) + ": arc movement in line " + str(index))

    def add_tool_change(self, 
                        index: int):
        self.counter += 1
        print("Movement_Manager call no. " +  str(self.counter) + ": tool change in line " + str(index))