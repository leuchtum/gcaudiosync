from gcaudiosync.gcanalyser.lineextractor import Line_Extractor
from gcaudiosync.gcanalyser.cncparameter import CNC_Parameter
from gcaudiosync.gcanalyser.cncstatus import CNC_Status
from gcaudiosync.gcanalyser.gcodeline import G_Code_Line
from gcaudiosync.gcanalyser.pausemanager import Pause_Manager
from gcaudiosync.gcanalyser.frequencymanager import Frequency_Manager
from gcaudiosync.gcanalyser.toolchangemanager import Tool_Change_Manager
from gcaudiosync.gcanalyser.coolingmanager import Cooling_Manager
from gcaudiosync.gcanalyser.movementmanager import Movement_Manager
from gcaudiosync.gcanalyser.toolpathgenerator import Tool_Path_Generator
import gcaudiosync.gcanalyser.filefunctions as filefunc

import copy

class GCodeAnalyser: # must be global object
    
    total_time = 0

    g_code = []

    # Constructor
    def __init__(self, parameter_src: str):

        self.CNC_Parameter = CNC_Parameter(parameter_src)

        self.Line_Extractor = Line_Extractor()

        self.Frequency_Manager = Frequency_Manager()
        self.Pause_Manager = Pause_Manager()
        self.Tool_Change_Manager = Tool_Change_Manager()
        self.Cooling_Manager = Cooling_Manager()
        self.Tool_Path_Generator = Tool_Path_Generator()

        self.G_Code_Lines: G_Code_Line = []

        current_cnc_status = CNC_Status(start_position = True, CNC_Parameter = self.CNC_Parameter)

        self.Movement_Manager = Movement_Manager(self.CNC_Parameter, current_cnc_status)

    #################################################################################################
    # Methods

    # Method for analyse of g-code
    def analyse(self, g_code_src: str):

        # Read in the g_code
        self.g_code: list = filefunc.read_file(g_code_src)
        
        # Make a new status at the beginnig of the g-code
        current_cnc_status: CNC_Status = CNC_Status(start_position = True, CNC_Parameter = self.CNC_Parameter)

        # Go through all lines and create G_Code_Lines
        for index, line in enumerate(self.g_code):

            # Check if program end is reached
            if current_cnc_status.program_end_reached:
                break

            # Create the G_Code_Line
            current_line: G_Code_Line = G_Code_Line(line_index = index,
                                                    current_status = current_cnc_status, 
                                                    line = line, 
                                                    Line_Extractor = self.Line_Extractor,
                                                    CNC_Parameter = self.CNC_Parameter,
                                                    Frequency_Manager = self.Frequency_Manager,
                                                    Pause_Manager = self.Pause_Manager,
                                                    Tool_Change_Manager = self.Tool_Change_Manager,
                                                    Cooling_Manager = self.Cooling_Manager,
                                                    Movement_Manager = self.Movement_Manager)
            
            # Append new G_Code_line to the list of G_Code_Lines
            self.G_Code_Lines.append(current_line)
            
            # Update the current cnc status
            current_cnc_status = copy.deepcopy(current_line.line_status)

        self.Movement_Manager.all_lines_analysed()

        time_stamps: list = self.Movement_Manager.get_time_stamps()
        self.Frequency_Manager.update(time_stamps)
        self.Pause_Manager.update(time_stamps)

    # Method to generate the total tool path
    def generate_total_tool_path(self, fps: int):
        # Call method from the Tool_Path_Generator
        self.Tool_Path_Generator.generate_total_tool_path(fps, self.Movement_Manager, self.g_code)

    def plot_tool_path(self):
        self.Tool_Path_Generator.plot_tool_path()

    def set_start_time_and_total_time(self, 
                                      start_time: int,
                                      total_time: int):
        self.Movement_Manager.set_start_time_and_total_time(start_time,
                                                            total_time)
        
        time_stamps = self.Movement_Manager.get_time_stamps()
        self.Frequency_Manager.update(time_stamps)
        self.Pause_Manager.update(time_stamps)

    def adjust_start_time_of_g_code_line(self,
                                         line_index: int,
                                         start_time: int):
        self.Movement_Manager.adjust_start_time_of_g_code_line(line_index,
                                                               start_time)
        
        time_stamps = self.Movement_Manager.get_time_stamps()
        self.Frequency_Manager.update(time_stamps)
        self.Pause_Manager.update(time_stamps)

    def adjust_end_time_of_g_code_line(self,
                                       line_index: int,
                                       end_time: int):
        self.Movement_Manager.adjust_start_time_of_g_code_line(line_index+1,
                                                               end_time)
# End of class
#####################################################################################################
