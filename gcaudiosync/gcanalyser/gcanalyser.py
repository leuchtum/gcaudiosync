import copy

import gcaudiosync.gcanalyser.filefunctions as filefunc

from gcaudiosync.gcanalyser.cncparameter import CNCParameter
from gcaudiosync.gcanalyser.cncstatus import CNCStatus
from gcaudiosync.gcanalyser.coolingmanager import CoolingManager
from gcaudiosync.gcanalyser.frequencymanager import FrequencyManager
from gcaudiosync.gcanalyser.gcodeline import GCodeLine
from gcaudiosync.gcanalyser.lineextractor import LineExtractor
from gcaudiosync.gcanalyser.movementmanager import MovementManager
from gcaudiosync.gcanalyser.pausemanager import PauseManager
from gcaudiosync.gcanalyser.toolchangemanager import ToolChangeManager
from gcaudiosync.gcanalyser.toolpathgenerator import ToolPathGenerator

class GCodeAnalyser:
    """
    A class to analyze G-code files.

    Attributes:
    -----------
    total_time : int
        Total time of g-code in milliseconds.
    g_code : list[str]
        List to store the original g-code lines.
    CNC_Parameter : CNCParameter
        An object containing the CNC parameters.
    Line_Extractor : LineExtractor
        An object to extract information from a g-code-line.
    Frequency_Manager : FrequencyManager
        An object to manage the frequencies.
    Pause_Manager : Pause_Manager
        An object to manage pauses in the g-code.
    Tool_Change_Manager : ToolChangeManager
        An object to manage tool changes.
    Cooling_Manager : CoolingManager
        An object to manage cooling operations.
    Tool_Path_Generator : ToolPathGenerator
        An object to generate the tool path.
    G_Code_Lines : list[GCodeLine]
        List to store all the GCodeLine objects in order.
    Movement_Manager : MovementManager
        An object to manage movements based on the CNC parameters and current status.
    """

    # Class variables
    total_time: int = 0         # Total time of g-code in milliseconds
    g_code: list[str] = []      # Original g-code is stored in this list as strings         
    
    def __init__(self, 
                 parameter_src: str):
        """
        Initializes the GCodeAnalyser instance with necessary parameters and managers.

        Parameters:
        -----------
        parameter_src : str
            The source of the CNC parameters.
        """

        # Initialize the CNC parameters
        self.CNC_Parameter = CNCParameter(parameter_src)       # Get the CNC-Parameter  

        # Initialize various managers required for g-code analysis
        self.Line_Extractor = LineExtractor()                  # Create the Line_Extractor object (we need only one for the whole program)
        self.Frequency_Manager = FrequencyManager()            # Create the Frequency_Manager object (we need only one for the whole program)
        self.Pause_Manager = PauseManager()                    # Create the Pause_Manager object (we need only one for the whole program)
        self.Tool_Change_Manager = ToolChangeManager()         # Create the Tool_Change_Manager object (we need only one for the whole program)
        self.Cooling_Manager = CoolingManager()                # Create the Cooling_Manager object (we need only one for the whole program)
        self.Tool_Path_Generator = ToolPathGenerator()         # Create the Tool_Path_Generator object (we need only one for the whole program)

        # Initialize the list to store G_Code_Line objects in order
        self.G_Code_Lines = []      

        # Create the initial CNC_Status object for the initialization of the MovementManager object
        current_cnc_status = CNCStatus(start_position = True, 
                                       CNC_Parameter = self.CNC_Parameter)

        # Create the Movement_Manager object (we need only one for the whole program)
        self.Movement_Manager = MovementManager(self.CNC_Parameter, 
                                                 current_cnc_status)

    #################################################################################################
    # Methods

    def analyse(self, 
                g_code_src: str):
        """
        Analyzes the G-code from the provided source file.

        Parameters:
        -----------
        g_code_src : str
            The path to the source file containing the G-code.

        Notes:
        ------
        This method reads the G-code from the file, processes each line to create GCodeLine
        objects, updates the CNC status, and informs relevant managers.
        """

        # Read in the g_code from the specified source file
        self.g_code: list[str] = filefunc.read_file(g_code_src)
        
        # Initialize the CNC status at the beginning of the G-code
        current_cnc_status: CNCStatus = CNCStatus(start_position = True, 
                                                  CNC_Parameter = self.CNC_Parameter)

        # Process each line of the G-code
        for g_code_line_index, g_code_line in enumerate(self.g_code):

            # Check if the end of the program is reached
            if current_cnc_status.program_end_reached:
                break

            # Create a G_Code_Line object for the current line
            current_line: GCodeLine = GCodeLine(line_index = g_code_line_index,
                                                current_status = current_cnc_status, 
                                                line = g_code_line, 
                                                Line_Extractor = self.Line_Extractor,
                                                CNC_Parameter = self.CNC_Parameter,
                                                Frequency_Manager = self.Frequency_Manager,
                                                Pause_Manager = self.Pause_Manager,
                                                Tool_Change_Manager = self.Tool_Change_Manager,
                                                Cooling_Manager = self.Cooling_Manager,
                                                Movement_Manager = self.Movement_Manager)
            
            # Append the new G_Code_Line object to the list
            self.G_Code_Lines.append(current_line)
            
            # Update the current CNC status
            current_cnc_status = copy.deepcopy(current_line.line_status)

        # Inform the Movement_Manager that all lines have been analyzed
        self.Movement_Manager.all_lines_analysed()

        # Get the time stamps of all movements
        time_stamps: list[int] = self.Movement_Manager.get_time_stamps()

        # Update the Frequency_Manager with the time stamps
        self.Frequency_Manager.update(time_stamps)

    def generate_tool_path(self, 
                                 fps: int):
        """
        Generates the tool path for the G-code.

        Parameters:
        -----------
        fps : int
            Frames per second for the tool path generation.

        Notes:
        ------
        This method uses the Tool_Path_Generator to generate the complete tool path
        based on the frames per second (fps) and the movements managed by Movement_Manager.
        The original G-code is also passed to the generator for reference.
        """
        # Generate the tool path using the Tool_Path_Generator
        self.Tool_Path_Generator.generate_total_tool_path(fps, 
                                                          self.Movement_Manager, 
                                                          self.g_code)

    def plot_tool_path(self):
        """
        Plots the tool path using the Tool_Path_Generator.

        Notes:
        ------
        This method instructs the Tool_Path_Generator to plot the tool path
        based on the analyzed G-code and generated tool paths.
        """
        # Inform the Tool_Path_Generator to plot the tool path
        self.Tool_Path_Generator.plot_tool_path()   

    def set_start_time_and_total_time(self, 
                                      start_time: int,
                                      total_time: int):
        """
        Sets the start time and total time for the movement manager and updates managers.

        Parameters:
        -----------
        start_time : int
            The start time for the tool path in milliseconds.
        total_time : int
            The total time for the tool path in milliseconds.

        Notes:
        ------
        This method updates the Movement_Manager with the provided start time and total time,
        then gets new time stamps and updates the Frequency_Manager and Pause_Manager accordingly.
        """

        # Inform the Movement_Manager of the start time and total time
        self.Movement_Manager.set_start_time_and_total_time(start_time,
                                                            total_time)
        
        # Get the new time stamps of all movements
        time_stamps: list[int] = self.Movement_Manager.get_time_stamps()
        
        # Update the Frequency_Manager with the new time stamps
        self.Frequency_Manager.update(time_stamps)
        
        # Update the Pause_Manager with the new time stamps
        self.Pause_Manager.update(time_stamps)

    def adjust_start_time_of_g_code_line(self,
                                         line_index: int,
                                         start_time: int):
        """
        Adjusts the start time of a specific G-code line.

        Parameters:
        -----------
        line_index : int
            The index of the G-code line to adjust.
        start_time : int
            The new start time for the specified G-code line in milliseconds.

        Notes:
        ------
        This method informs the Movement_Manager to adjust the start time of the specified G-code line.
        It then updates the time stamps and informs the Frequency_Manager and Pause_Manager of the changes.
        """
        # Inform Movement_Manager to adjust the start time of the specified G-code line
        self.Movement_Manager.adjust_start_time_of_g_code_line(line_index,
                                                               start_time)
        
        # Get the new time stamps of all movements
        time_stamps: list[int] = self.Movement_Manager.get_time_stamps()
        
        # Update the Frequency_Manager with the new time stamps
        self.Frequency_Manager.update(time_stamps)
        
        # Update the Pause_Manager with the new time stamps
        self.Pause_Manager.update(time_stamps)

    def adjust_end_time_of_g_code_line(self,
                                       g_code_line_index: int,
                                       end_time: int):
        """
        Adjusts the end time of a specific G-code line.

        Parameters:
        -----------
        g_code_line_index : int
            The index of the G-code line to adjust.
        end_time : int
            The new end time for the specified G-code line in milliseconds.

        Notes:
        ------
        This method informs the Movement_Manager to adjust the start time of the next G-code line (line_index + 1)
        to set the end time of the specified G-code line. It's assumed that the end time of a line corresponds
        to the start time of the next line.
        """
        # Inform Movement_Manager to adjust the start time of the next G-code line to set the end time of the specified line
        self.Movement_Manager.adjust_end_time_of_g_code_line(g_code_line_index,
                                                             end_time)
        
# End of class
#####################################################################################################
