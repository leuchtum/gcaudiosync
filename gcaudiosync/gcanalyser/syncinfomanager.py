import copy
import numpy as np

from typing import List, Tuple

import gcaudiosync.gcanalyser.filefunctions as filefunc

from gcaudiosync.gcanalyser.cncparameter import CNCParameter
from gcaudiosync.gcanalyser.frequencyinformation import FrequencyInformation
from gcaudiosync.gcanalyser.lineextractor import LineExtractor
from gcaudiosync.gcanalyser.snapshotinformation import SnapshotInformation


class SyncInfoManager:
    """
    Manages information extracted from G-code files related to synchronization tasks.

    Attributes:
        tool_change_information: List[int]
            List of line indices where tool changes occur.
        cooling_information: List
            List containing information about coolant activation/deactivation (TODO: Not currently implemented).
        frequency_information: List[FrequencyInformation] 
            List of FrequencyInformation objects storing details about spindle speed segments.
        pause_information: List
            List containing information about pauses (line index, type, timestamp - partially implemented).
        snapshot_information: List[SnapshotInformation]
            List of SnapshotInformation objects containing details about identified snapshots.
        snapshot_length: int
            Number of lines in the snapshot G-code definition.
        snapshot_frequency: int
            Spindle speed (Hz) extracted from the snapshot G-code definition.
        g_code_line_index_with_start_of_snapshot: List[int]
            List of line indices where snapshots begin in the main G-code file.
        last_spindle_status: int
            Integer representing the last known spindle status (0: off, 3: clockwise, 4: counter-clockwise).
        f: int:
            The current spindle speed (Hz).
        current_g_code_line_index: int
            The current line index being processed in the main G-code file.

    """

    # Constructor
    def __init__(self,
                 snapshot_src: str,
                 Line_Extractor: LineExtractor,
                 CNC_Parameter: CNCParameter):
        """
        Initializes the CNCStatus SyncInfoManager.

        Parameters:
        ----------
        snapshot_src: str
            Path to the G-code file containing snapshot definitions.
        Line_Extractor: LineExtractor
            An instance of a class used to extract information from individual G-code lines.
        CNC_Parameter: CNCParameter
            An instance of a class holding parameters related to the CNC machine (e.g., S value limits).
        """

        self.Line_Extractor = Line_Extractor

        # Generate all the Lists with the information
        self.tool_change_information = []
        self.cooling_information = []
        self.frequency_information: List[FrequencyInformation] = []
        self.pause_information = []
        self.snapshot_information: List[SnapshotInformation] = []

        ###############################################################
        # stuff for the snapshot info

        self.snapshot_length: int
        self.snapshot_frequency: int # [Hz]

        # Read in the snapshot pause and handle it
        snapshot_g_code: List[str] = filefunc.read_file(snapshot_src)

        # get the g-code and length for the snapshot
        self.snapshot_g_code = get_snapshot(snapshot_g_code)
        self.snapshot_length = len(snapshot_g_code)

        # List with indices with the start of a snapshot
        self.g_code_line_index_with_start_of_snapshot: List[int] = []

        # Get frequency information
        for snapshot_line_index in range(self.snapshot_length):
            snapshot_line_info = self.Line_Extractor.extract(line = copy.copy(self.snapshot_g_code[snapshot_line_index]))

            for snapshot_line_info_index in range(len(snapshot_line_info)):
                if snapshot_line_info[snapshot_line_info_index][0] == "S" and float(snapshot_line_info[snapshot_line_info_index][1]) > 0:
                    S_value = float(snapshot_line_info[snapshot_line_info_index][1])

                    # Determine and set the new S value based on CNC parameters
                    if CNC_Parameter.S_IS_ABSOLUTE:
                        # S value is absolute
                        if S_value > CNC_Parameter.S_MAX:
                            raise Exception(f"S value in snapshot is too high.")
                    else: 
                        # S value is relative
                        if S_value > 100:
                            raise Exception(f"Error in gcode line: Relative S value > 100")
                        S_value = CNC_Parameter.S_MAX * S_value / 100.0           # Set the valid S value

                    # Set frequency
                    self.snapshot_frequency = int(S_value / 60)

                    break

        ###############################################################
        # stuff for the frequency info
        self.last_spindle_status: int = 0  # 0 -> off, 2 -> CW, 3 -> CCW
        self.f: int = 0
        self.current_g_code_line_index: int = 0

        new_frequency_information = FrequencyInformation(0, 0, 0, 0)
        self.frequency_information.append(new_frequency_information)

    #################################################################################################
    # Methods for snapshot info

    def check_start_of_snapshot(self,
                                g_code_line_index: int,
                                g_code_lines_for_snapshot: List[str]) -> bool:
        """
        Checks if the given g-code line starts a snapshot.

        Args:
            g_code_line_index (int): Index of the current g-code line.
            g_code_lines_for_snapshot (List[str]): List of g-code lines to compare with the snapshot definition.

        Returns:
            bool: True if the line starts a snapshot, False otherwise.
        """
        
        # Iterate through all lines of the snapshot
        for snapshot_line_index in range(self.snapshot_length):
            snapshot_info: List[str] = self.Line_Extractor.extract(self.snapshot_g_code[snapshot_line_index])
            g_code_line_info: List[str] = self.Line_Extractor.extract(line = g_code_lines_for_snapshot[snapshot_line_index])            # Extract info from line

            # Get rid of line number in g_code_line_info
            for g_code_line_info_index in range(len(g_code_line_info)):
                if g_code_line_info[g_code_line_info_index][0] == "N":
                    g_code_line_info.pop(g_code_line_info_index)
                    break
            
            # check if lengh of the two infos matches
            if len(snapshot_info) != len(g_code_line_info):
                return False
            
            # Iterate through all info and search for diffrences
            for snapshot_info_index in range(len(snapshot_info)):
                command_snapshot = snapshot_info[snapshot_info_index][0]
                command_g_code = g_code_line_info[snapshot_info_index][0]
                number_of_command_snapchot = snapshot_info[snapshot_info_index][1]
                number_of_command_g_code = g_code_line_info[snapshot_info_index][1]

                if command_snapshot != command_g_code or number_of_command_snapchot != number_of_command_g_code:
                    return False
                
        self.g_code_line_index_with_start_of_snapshot.append(g_code_line_index)

        return True

    def add_snapshot(self,
                     g_code_line_index: int) -> None:
        """
        Adds a snapshot that appears in a g-code-line.

        Args:
            g_code_line_index (int): Index of the g-code line where the snapshot starts.
        """

        new_snapshot = SnapshotInformation(g_code_line_index_start = g_code_line_index)

        self.snapshot_information.append(new_snapshot)

    #################################################################################################
    # Methods for tool change info
    def new_Tool(self, 
                 g_code_line_index: int):

        """
        Adds a tool change.

        Parameters:
        -----------
        g_code_line_index : int
            The current line index in the G-code.
        """

        self.tool_change_information.append(g_code_line_index)

    #################################################################################################
    # Methods for frequency info

    def new_S(self, 
              g_code_line_index: int, 
              new_S_value: int) -> None:
        """
        Updates the frequency based on a new S command in the G-code.

        Parameters:
        -----------
        g_code_line_index : int
            The current line index in the G-code.
        new_S_value : int
            The new S value indicating the spindle speed.
        """

        new_f: int = int(new_S_value / 60)     # Compute frequency in Hz

        # Check if new frequency needed
        if self.last_spindle_status != 0 and new_f != self.f:

            if self.current_g_code_line_index != g_code_line_index:
                # New frequency needed

                # End last frequency
                self.frequency_information[-1].g_code_line_index_end = (g_code_line_index-1)                            

                # Make new frequency
                new_frequency_information = FrequencyInformation(g_code_line_index_start = g_code_line_index,
                                                                 g_code_line_index_end = g_code_line_index,
                                                                 frequency = new_f, 
                                                                 spindle_status = self.last_spindle_status)
                self.frequency_information.append(new_frequency_information)
            else: 
                # Last frequency needs to change
                self.frequency_information[-1].frequency = new_f

        # Update attributes
        self.f = new_f
        self.current_g_code_line_index = g_code_line_index

    def new_Spindle_Operation(self, 
                              g_code_line_index: int, 
                              spindle_command: str) -> None:
        """
        Updates the spindle status based on a new spindle operation command.

        Parameters:
        -----------
        g_code_line_index : int
            The current line index in the G-code.
        spindle_command : str
            The spindle operation command ('off', 'CW', 'CCW').
        """

        new_spindle_status: int = 0

        # Check command
        match spindle_command:
            case "off":
                pass
            case "CW":
                new_spindle_status = 3
            case "CCW":
                new_spindle_status = 4

        if self.last_spindle_status != new_spindle_status:
            # Something has to change

            # End last frequency
            self.frequency_information[-1].g_code_line_index_end = (g_code_line_index-1)

            # Create new frequency information based on spindle status
            if new_spindle_status == 0:                 # spindle turns off
                new_frequency_information = FrequencyInformation(g_code_line_index_start = g_code_line_index,
                                                                 g_code_line_index_end = g_code_line_index,
                                                                 frequency = 0, 
                                                                 spindle_status = new_spindle_status)
            elif self.last_spindle_status == 0:         # spindle turns on
                new_frequency_information = FrequencyInformation(g_code_line_index_start = g_code_line_index,
                                                                 g_code_line_index_end = g_code_line_index,
                                                                 frequency = self.f, 
                                                                 spindle_status = new_spindle_status)                
            else:                                       # spindle changes direction
                new_frequency_information = FrequencyInformation(g_code_line_index_start = g_code_line_index,
                                                                 g_code_line_index_end = g_code_line_index,
                                                                 frequency = self.f, 
                                                                 spindle_status = new_spindle_status)     

            # Add new frequency information
            self.frequency_information.append(new_frequency_information)

            # Update attributes
            self.last_spindle_status = new_spindle_status
            self.current_g_code_line_index = g_code_line_index

    #################################################################################################
    # Methods for pause info

    def new_dwell(self, 
                  g_code_line_index: int, 
                  time: int):

        """
        Adds a dwell time.

        Parameters:
        -----------
        g_code_line_index : int
            The current line index in the G-code.
        time : int
            Time of the dwell in ms.
        """

        self.pause_information.append(np.array([g_code_line_index, 4, 0, time]))

    def new_pause(self, 
                  g_code_line_index: int, 
                  kind_of_pause: int):

        """
        Adds a pause.

        Parameters:
        -----------
        g_code_line_index : int
            The current line index in the G-code.
        kind_of_pause : int
            Kind of pause used here
        """
        # here it might be good to inform the frequancy manager that the spindle could stand still. not implemented jet
        # or frequency-manager looks over all pauses at the end.

        self.pause_information.append(np.array([g_code_line_index, kind_of_pause, 0, -1]))

    #################################################################################################
    # Methods for updateing all informaiton

    def update(self,
               time_stamps: List[Tuple[int, int]]) -> None:
        """
        Updates all time stamps.

        Parameters:
        -----------
        time_stamps : List[Tuple[int, int]]
            List with Toupels of the G-Code-line and the timestamp
        """

        time_stamp_index: int = 0

        # Update frequencies
        for frequency in self.frequency_information:
            index_start = frequency.g_code_line_index_start
            index_end = frequency.g_code_line_index_end

            # Find the start time for the current frequency segment
            for index in range(time_stamp_index, len(time_stamps)):
                if time_stamps[index][0] >= index_start:
                    time_stamp_index = index
                    break
            
            frequency.expected_time_start = time_stamps[time_stamp_index][1]

            # Find the end time for the current frequency segment
            for index in range(time_stamp_index, len(time_stamps)):
                if time_stamps[index][0] >= index_end:
                    time_stamp_index = index
                    break
            
            frequency.expected_duration = time_stamps[time_stamp_index][1] - frequency.expected_time_start
        
        # update pauses
        for pause in self.pause_information:
            time_stamp_index = 0
            pause_index = pause[0]

            for index in range(time_stamp_index, len(time_stamps)):
                if time_stamps[index][0] >= pause_index:
                    time_stamp_index = index
                    break

            pause[2] = time_stamps[time_stamp_index][1]

        # update snapshots
        for snapshot in self.snapshot_information:
            time_stamp_index = 0
            snapshot_g_code_index = snapshot.g_code_line_index_start

            # Find the start time for the current snapshot
            for index in range(time_stamp_index, len(time_stamps)):
                if time_stamps[index][0] >= snapshot_g_code_index:
                    time_stamp_index = index
                    break
            
            snapshot.expected_time_start = time_stamps[time_stamp_index][1]

        # TODO: update cooling
        # TODO: update tool change

    #################################################################################################
    # Methods for printing infos

    def frequency_info(self) -> None:
        """
        Print the information of the frequencies
        """

        print(f"Total: {len(self.frequency_information)} frequencies\n")

        for frequence_info in self.frequency_information:
            frequence_info.print_info()
            print("")

    def snapshot_info(self) -> None:
        """
        Print the information of the snapshots
        """

        print(f"Total: {len(self.snapshot_information)} snapshots+")

        for snapshot_info in self.snapshot_information:
            snapshot_info.info()

# End of class
#####################################################################################################



def get_snapshot(g_code_list: List[str]) -> List[str]:
    """
    Function to get the G-Code of the snapshot.

    Parameters:
    ----------
        g_code_list : List[str]
            List of G-Code-Lines of the snapshot-file.
    
    Retruns:
    -------
        List[str]
            Useable list of G-Code lines containing the snapshot.
    """

    g_code_line_index = 0

    # Remove all spaces and \n
    for g_code_line_index in range(len(g_code_list)):
        g_code_list[g_code_line_index] = g_code_list[g_code_line_index].strip("\n")     # Remove the \n at the end of the line if it is there
        g_code_list[g_code_line_index] = g_code_list[g_code_line_index].upper()         # Make all letters capital

    # remove all comments starting with a ; and empty lines
    g_code_line_index = 0
    while g_code_line_index < len(g_code_list):
        if g_code_list[g_code_line_index] == "":
            g_code_list.pop(g_code_line_index)
        elif g_code_list[g_code_line_index][0] == ";":
            g_code_list.pop(g_code_line_index)
        else:
            g_code_line_index += 1

    return g_code_list