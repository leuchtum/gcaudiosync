import copy

from typing import List

import gcaudiosync.gcanalyser.filefunctions as filefunc

from gcaudiosync.gcanalyser.cncparameter import CNCParameter
from gcaudiosync.gcanalyser.lineextractor import LineExtractor
from gcaudiosync.gcanalyser.snapshotinformation import SnapshotInformation

class SnapshotManager:
    
    # Class Parameter
    snapshot_length: int
    snapshot_frequency: int # [Hz]

    # Constructor
    def __init__(self,
                 snapshot_src: str,
                 Line_Extractor: LineExtractor,
                 CNC_Parameter: CNCParameter):
        
        self.Line_Extractor = Line_Extractor

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

    #################################################################################################
    # Methods

    def check_start_of_snapshot(self,
                                g_code_line_index: int,
                                g_code_lines_for_snapshot: List[str]):
        
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

    #TODO
    def update(self,
               time_stamps: List):
        pass

    def print_information(self):
        print(f"Snapshots in the following g-code-line-indexes:")
        print(self.g_code_line_index_with_start_of_snapshot)

# End of class
#####################################################################################################


# Function that goes through a list and deletes every entity of list that starts with a ;
def get_snapshot(g_code_list: List[str]) -> List[str]:
    
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
