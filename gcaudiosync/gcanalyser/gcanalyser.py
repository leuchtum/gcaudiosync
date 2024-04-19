from gcaudiosync.gcanalyser.lineextractor import LineExtractor
from gcaudiosync.gcanalyser.cncparameter import CNC_Parameter
from gcaudiosync.gcanalyser.filefunctions import *

class GCodeAnalyser:   
    
    # Constructor
    def __init__(self, parameter_src):

        self.CNC_Parameter = CNC_Parameter(parameter_src)

        self.Extractor = LineExtractor()


    #################################################################################################
    # Methods

    # TODO: work and comment
    def analyse(self, g_code_src):

        # read in the g_code
        self.g_code = read_file(g_code_src)

        # make something like an object for the current movement and the last movement
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
    

# end of class
#####################################################################################################