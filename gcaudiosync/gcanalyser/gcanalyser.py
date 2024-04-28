from gcaudiosync.gcanalyser.lineextractor import LineExtractor
from gcaudiosync.gcanalyser.cncparameter import CNC_Parameter
from gcaudiosync.gcanalyser.cncstatus import CNC_Status
from gcaudiosync.gcanalyser.gcodeline import G_Code_Line
from gcaudiosync.gcanalyser.pausemanager import Pause_Manager
from gcaudiosync.gcanalyser.frequencymanager import Frequency_Manager
from gcaudiosync.gcanalyser.toolchangemanager import Tool_Change_Manager
from gcaudiosync.gcanalyser.coolingmanager import Cooling_Manager
from gcaudiosync.gcanalyser.movementmanager import Movement_Manager
import gcaudiosync.gcanalyser.filefunctions as filefunc

import copy

class GCodeAnalyser: # must be global object
    
    # Constructor
    def __init__(self, parameter_src):

        self.CNC_Parameter = CNC_Parameter(parameter_src)

        self.Extractor = LineExtractor()

        self.Frequancy_Manager = Frequency_Manager()
        self.Pause_Manager = Pause_Manager()
        self.Tool_Change_Manager = Tool_Change_Manager()
        self.Cooling_Manager = Cooling_Manager()

        self.Events: G_Code_Line = []

    #################################################################################################
    # Methods

    # TODO: work and comment
    def analyse(self, g_code_src):

        # read in the g_code
        self.g_code = filefunc.read_file(g_code_src)

        current_cnc_status = CNC_Status(start_position = True, CNC_Parameter = self.CNC_Parameter)

        self.Movement_Manager = Movement_Manager(current_cnc_status)

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
            
            self.Events.append(current_line)
            
            if index >= 1:
                last_line_status = copy.deepcopy(current_line.last_line_status)
                self.Events[index-1].line_status = last_line_status

            current_cnc_status = copy.deepcopy(current_line.line_status)

        self.update_Manager_time()
            
        # make something like an object for the current line and the last line
        # make an object/list for: events
        # objects in events: lin_movement, arc_movement, dewll, pause, spindle_change, tool_change
        # objects for synchronisation: dewll_times/pause/tool_change, frequencys, S_change
        # initialize start position

        # for loop over all lines

            # for loop over all information in the line

            # g -> 
            # x,y,z,i,j,k,r
            # m

        return 0
    
    # TODO
    def update_Manager_time(self):
        pass

# end of class
#####################################################################################################