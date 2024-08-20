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
    total_time : float
        Total time of g-code in milliseconds.
    g_code : List[str]
        List to store the original g-code lines.
    CNC_Parameter : CNCParameter
        An object containing the CNC parameters.
    Line_Extractor : LineExtractor
        An object to extract information from a g-code-line.
    Tool_Path_Generator : ToolPathGenerator
        An object to generate the tool path.
    g_code_lines : List[GCodeLine]
        List to store all the GCodeLine objects in order.
    Sync_Info_Manager: SyncInfoManager
        An object to manage all information needed for the synchronisation.
    Movement_Manager : MovementManager
        An object to manage movements based on the CNC parameters and current status.
    """

    # Constructor
    def __init__(self, 
                 parameter_src: str,
                 snapshot_src: str):
        """
        Initializes the GCodeAnalyser instance with necessary parameters and managers.

        Parameters:
        -----------
        parameter_src : str
            The source path of the CNC parameters.
        snapshot_pause_src : str
            The source path of the snapshot pause code
        """

        self.total_duration: float = 0           # Total time of g-code in milliseconds
        self.g_code: List[str] = []              # Original g-code is stored in this list as strings      
        self.g_code_lines: List[GCodeLine] = []  # Initialize the list to store GCodeLine objects in order
    

        # Initialize the CNC parameters
        self.CNC_Parameter: CNCParameter = CNCParameter(parameter_src)

        # Initialize the managers and objects required for g-code analysis
        self.Line_Extractor: LineExtractor          = LineExtractor()                
        self.Tool_Path_Generator: ToolPathGenerator = ToolPathGenerator()   
        self.Sync_Info_Manager: SyncInfoManager     = SyncInfoManager(snapshot_src = snapshot_src,
                                                                      Line_Extractor = self.Line_Extractor,
                                                                      CNC_Parameter = self.CNC_Parameter)    
        self.Movement_Manager: MovementManager      = MovementManager(CNC_Parameter = self.CNC_Parameter)

    #################################################################################################
    # Methods

    def analyse(self, 
                g_code_src: str) -> None:
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
        snapshot_index: int = -1    # Set snapshot-index to -1: no snapshot
        for g_code_line_index, g_code_line in enumerate(self.g_code):

            # Check if the end of the program is reached
            if current_cnc_status.program_end_reached:
                break
            
            # Check for snapshot
            if snapshot_index == -1:    # snapshot possible
                # Set possible start and end of a snapshot (excluded end)
                possible_start_of_snapshot = g_code_line_index
                possible_end_of_snapshot = possible_start_of_snapshot + self.Sync_Info_Manager.snapshot_length

                # Check snapshot
                if possible_end_of_snapshot <= len(self.g_code):
                    g_code_lines_for_possible_snapshot = copy.copy(self.g_code[possible_start_of_snapshot:possible_end_of_snapshot]) # Get g-code
                    # Check for snapshot
                    if self.Sync_Info_Manager.check_start_of_snapshot(g_code_line_index = g_code_line_index, 
                                                                      g_code_lines_for_snapshot = g_code_lines_for_possible_snapshot):
                        snapshot_index = 0
                        self.Sync_Info_Manager.add_snapshot(g_code_line_index = g_code_line_index) # Inform Manager about snapshot
            elif snapshot_index < self.Sync_Info_Manager.snapshot_length-2: # g-code-line is part of a snapshot
                snapshot_index += 1
            else:   # snapshot has ended
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

        # Inform the Movement_Manager that all lines have been analyzed
        self.Movement_Manager.all_lines_analysed()

        # Get the time stamps of all movements
        time_stamps: List = self.Movement_Manager.get_time_stamps()

        # Update the Frequency_Manager with the time stamps
        self.Sync_Info_Manager.update(time_stamps)

        # Update time
        self.total_duration = self.Movement_Manager.total_duration + self.Movement_Manager.start_time

    def generate_tool_path(self, 
                           fps: int) -> None:
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
        self.Tool_Path_Generator.generate_total_tool_path(fps = fps, 
                                                          Movement_Manager = self.Movement_Manager, 
                                                          g_code = self.g_code)

    def plot_tool_path(self, version: str) -> None:
        """
        Plots the tool path using the Tool_Path_Generator.

        Parameters:
        -----------
        version: str
            Version of the plot. Available: Timo, Daniel

        Notes:
        ------
        This method instructs the Tool_Path_Generator to plot the tool path
        based on the analyzed G-code and generated tool paths.
        """
        
        # Inform the Tool_Path_Generator to plot the tool path
        if version == "Timo":
            self.Tool_Path_Generator.plot_tool_path_Timo()
        elif version == "Daniel":
            self.Tool_Path_Generator.plot_tool_path_Daniel()

    def set_start_time_and_total_time(self, 
                                      start_time: float,
                                      total_time: float) -> None:
        """
        Sets the start time and total time for the movement manager and updates managers.

        Parameters:
        -----------
        start_time : float
            The start time for the tool path in milliseconds.
        total_time : float
            The total time for the tool path in milliseconds.

        Notes:
        ------
        This method updates the Movement_Manager with the provided start time and total time,
        then gets new time stamps and updates the Frequency_Manager and Pause_Manager accordingly.
        """

        # Inform the Movement_Manager of the start time and total time
        self.Movement_Manager.set_start_time_and_duration(new_start_time = start_time,
                                                            new_total_duration = total_time)
        
        # Get the new time stamps of all movements
        time_stamps: List = self.Movement_Manager.get_time_stamps()
        
        # Update the Manager with the new time stamps
        self.Sync_Info_Manager.update(time_stamps)

        # Update the time
        self.total_duration = self.Movement_Manager.total_duration + self.Movement_Manager.start_time
 
    def adjust_start_time_of_g_code_line(self,
                                         g_code_line_index: int,
                                         start_time: float):
        """
        Adjusts the start time of a specific G-code line.

        Parameters:
        -----------
        g_code_line_index : int
            The index of the G-code line to adjust.
        start_time : float
            The new start time for the specified G-code line in milliseconds.

        Notes:
        ------
        This method informs the Movement_Manager to adjust the start time of the specified G-code line.
        It then updates the time stamps and informs the Frequency_Manager and Pause_Manager of the changes.
        """

        # Inform Movement_Manager to adjust the start time of the specified G-code line
        self.Movement_Manager.adjust_start_time_of_g_code_line(g_code_line_index = g_code_line_index,
                                                               new_start_time = start_time)
        
        # Get the new time stamps of all movements
        time_stamps: List = self.Movement_Manager.get_time_stamps()
        
        # Update the Managers with the new time stamps
        self.Sync_Info_Manager.update(time_stamps)

    def adjust_end_time_of_g_code_line(self,
                                       g_code_line_index: int,
                                       end_time: float):
        """
        Adjusts the end time of a specific G-code line.

        Parameters:
        -----------
        g_code_line_index : int
            The index of the G-code line to adjust.
        end_time : float
            The new end time for the specified G-code line in milliseconds.

        Notes:
        ------
        This method informs the Movement_Manager to adjust the start time of the next G-code line (line_index + 1)
        to set the end time of the specified G-code line. It's assumed that the end time of a line corresponds
        to the start time of the next line.
        """

        # Inform Movement_Manager to adjust the start time of the next G-code line to set the end time of the specified line
        self.Movement_Manager.adjust_end_time_of_g_code_line(g_code_line_index = g_code_line_index,
                                                             new_end_time = end_time)
        
        # Get the new time stamps of all movements
        time_stamps: List = self.Movement_Manager.get_time_stamps()
        
        # Update the Managers with the new time stamps
        self.Sync_Info_Manager.update(time_stamps)
        
    def print_info(self):
        """
        Prints the info of the GCAnalydser
        """

        if self.g_code == []:
            print(f"No g-code analysed.")
        else:
            print(f"Analysed g-code:")
            for g_code_line in self.g_code:
                print("    " + g_code_line)
            print("")
            print(f"Total duration: {int(self.total_duration/1000)} s")
            print(f"Number of movements: {len(self.Movement_Manager.movements)}")
            print(f"Number of frequencies: {len(self.Sync_Info_Manager.frequency_information)}")
            print(f"Number of snapshots: {len(self.Sync_Info_Manager.snapshot_information)}")
            print("")

# End of class
#####################################################################################################
