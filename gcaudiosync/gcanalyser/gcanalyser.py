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

        return 0
    

# end of class
#####################################################################################################