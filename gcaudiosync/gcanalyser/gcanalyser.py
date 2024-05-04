from gcaudiosync.gcanalyser.lineextractor import LineExtractor
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
    
    expected_time_total = 0

    g_code = []

    # Constructor
    def __init__(self, parameter_src):

        self.CNC_Parameter = CNC_Parameter(parameter_src)

        self.Extractor = LineExtractor()

        self.Frequancy_Manager = Frequency_Manager()
        self.Pause_Manager = Pause_Manager()
        self.Tool_Change_Manager = Tool_Change_Manager()
        self.Cooling_Manager = Cooling_Manager()
        self.Tool_Path_Generator = Tool_Path_Generator()

        self.G_Code_Lines: G_Code_Line = []

        current_cnc_status = CNC_Status(start_position = True, CNC_Parameter = self.CNC_Parameter)

        self.Movement_Manager = Movement_Manager(self.CNC_Parameter, current_cnc_status)

    #################################################################################################
    # Methods

    # TODO: work and comment
    def analyse(self, g_code_src):

        # read in the g_code
        self.g_code = filefunc.read_file(g_code_src)

        current_cnc_status = CNC_Status(start_position = True, CNC_Parameter = self.CNC_Parameter)

        for index, line in enumerate(self.g_code):
            
            line_info = self.Extractor.extract(line=line)

            current_line = G_Code_Line(index = index,
                                       current_status = current_cnc_status, 
                                       line_info = line_info, 
                                       CNC_Parameter = self.CNC_Parameter,
                                       Frequancy_Manager = self.Frequancy_Manager,
                                       Pause_Manager = self.Pause_Manager,
                                       Tool_Change_Manager = self.Tool_Change_Manager,
                                       Cooling_Manager = self.Cooling_Manager,
                                       Movement_Manager = self.Movement_Manager)
            
            self.G_Code_Lines.append(current_line)
            
            # if index >= 1:
            #   last_line_status = copy.deepcopy(current_line.last_line_status)
            #   self.G_Code_Lines[index-1].line_status = last_line_status

            current_cnc_status = copy.deepcopy(current_line.line_status)

        self.Movement_Manager.update_vectors_linear_of_movements()
        self.expected_time_total = self.get_expected_time_total()
            
        return 0

    def get_expected_time_total(self):

        expected_time_total = 0

        for G_Code_Line in self.G_Code_Lines:
            expected_time_total += G_Code_Line.expected_time

        return expected_time_total

    def generate_total_tool_path(self, delta_time):
        self.Tool_Path_Generator.generate_total_tool_path(delta_time, self.expected_time_total, self.Movement_Manager)

    def plot_tool_path(self):
        self.Tool_Path_Generator.plot_tool_path()

# end of class
#####################################################################################################