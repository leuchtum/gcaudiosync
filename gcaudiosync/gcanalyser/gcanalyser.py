import copy

from typing import List

import gcaudiosync.gcanalyser.filefunctions as filefunc

from gcaudiosync.gcanalyser.cncparameter import CNCParameter
from gcaudiosync.gcanalyser.cncstatus import CNCStatus
from gcaudiosync.gcanalyser.gcodeline import GCodeLine
from gcaudiosync.gcanalyser.lineextractor import LineExtractor
from gcaudiosync.gcanalyser.movementmanager import MovementManager
from gcaudiosync.gcanalyser.syncinfomanager import SyncInfoManager
from gcaudiosync.gcanalyser.toolpathgenerator import ToolPathGenerator

class GCodeAnalyser:
    """
    A class to analyze G-code files.

    Attributes:
    -----------
    total_time : int
        Total time of g-code in milliseconds.
    g_code : List[str]
        List to store the original g-code lines.
    CNC_Parameter : CNCParameter
        An object containing the CNC parameters.
    Line_Extractor : LineExtractor
        An object to extract information from a g-code-line.
    Tool_Path_Generator : ToolPathGenerator
        An object to generate the tool path.
    G_Code_Lines : List[GCodeLine]
        List to store all the GCodeLine objects in order.
    Sync_Info_Manager: SyncInfoManager
        An object to manage all information needed for the synchronisation
    Movement_Manager : MovementManager
        An object to manage movements based on the CNC parameters and current status.
    """

    # Class variables
    total_time: int = 0                 # Total time of g-code in milliseconds
    g_code: List[str] = []              # Original g-code is stored in this list as strings      
    g_code_lines: List[GCodeLine] = []  # Initialize the list to store GCodeLine objects in order
    
    # Constructor
    def __init__(self, 
                 parameter_src: str,
                 snapshot_src: str):
        """
        Initializes the GCodeAnalyser instance with necessary parameters and managers.

        Parameters:
        -----------
        parameter_src : str
            The source of the CNC parameters.
        snapshot_pause_src : str
            The source of the snapshot pause code
        """

        # Initialize the CNC parameters
        self.CNC_Parameter: CNCParameter = CNCParameter(parameter_src)       # Get the CNC-Parameter  

        # Initialize various managers required for g-code analysis
        self.Line_Extractor: LineExtractor = LineExtractor()                   # Create the Line_Extractor object (we need only one for the whole program)
        self.Tool_Path_Generator: ToolPathGenerator = ToolPathGenerator()          # Create the Tool_Path_Generator object (we need only one for the whole program)
        
        # Create the Info Manager
        self.Sync_Info_Manager = SyncInfoManager(snapshot_src,
                                                 self.Line_Extractor,
                                                 self.CNC_Parameter)    

        # Create the Movement_Manager object (we need only one for the whole program)
        self.Movement_Manager: MovementManager = MovementManager(self.CNC_Parameter)

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
        self.g_code: List[str] = filefunc.read_file(g_code_src)

        # Initialize the CNC status at the beginning of the G-code
        current_cnc_status: CNCStatus = CNCStatus(start_position = True, 
                                                  CNC_Parameter = self.CNC_Parameter)

        # Process each line of the G-code
        snapshot_index: int = -1
        for g_code_line_index, g_code_line in enumerate(self.g_code):

            # Check if the end of the program is reached
            if current_cnc_status.program_end_reached:
                break
            
            # Check for snapshot
            if snapshot_index == -1:
                possible_start_of_snapshot = g_code_line_index
                possible_end_of_snapshot = possible_start_of_snapshot + self.Sync_Info_Manager.snapshot_length

                if possible_end_of_snapshot <= len(self.g_code):
                    g_code_lines_for_snapshot = copy.copy(self.g_code[possible_start_of_snapshot:possible_end_of_snapshot])
                    if self.Sync_Info_Manager.check_start_of_snapshot(g_code_line_index, 
                                                                     g_code_lines_for_snapshot):
                        snapshot_index = 0
            elif snapshot_index < self.Sync_Info_Manager.snapshot_length-2:
                snapshot_index += 1
            else:
                snapshot_index = -1

            # Create a G_Code_Line object for the current line
            current_line: GCodeLine = GCodeLine(g_code_line_index = g_code_line_index,
                                                current_cnc_status = current_cnc_status, 
                                                g_code_line = g_code_line, 
                                                Line_Extractor = self.Line_Extractor,
                                                CNC_Parameter = self.CNC_Parameter,
                                                Sync_Info_Manager = self.Sync_Info_Manager,
                                                Movement_Manager = self.Movement_Manager)
            
            # Append the new G_Code_Line object to the list
            self.g_code_lines.append(current_line)
            
            # Update the current CNC status
            current_cnc_status = copy.deepcopy(current_line.cnc_status_current_line)

            # Add snapshot information if this line is the start of a snapshot
            if snapshot_index == 0:
                pass

        # Inform the Movement_Manager that all lines have been analyzed
        self.Movement_Manager.all_lines_analysed()

        # Get the time stamps of all movements
        time_stamps: List = self.Movement_Manager.get_time_stamps()

        # Update the Frequency_Manager with the time stamps
        self.Sync_Info_Manager.update(time_stamps)

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
        self.Movement_Manager.set_start_time_and_total_time(new_start_time = start_time,
                                                            new_total_time = total_time)
        
        # Get the new time stamps of all movements
        time_stamps: List = self.Movement_Manager.get_time_stamps()
        
        # Update the Manager with the new time stamps
        self.Sync_Info_Manager.update(time_stamps)

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
        time_stamps: List = self.Movement_Manager.get_time_stamps()
        
        # Update the Managers with the new time stamps
        self.Sync_Info_Manager.update(time_stamps)


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
