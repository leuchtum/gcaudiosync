import numpy as np

from typing import List, Tuple

from gcaudiosync.gcanalyser.frequencyinformation import FrequencyInformation

class FrequencyManager:
    """
    A class to manage frequency information for G-code operations.

    Attributes:
    -----------
    last_spindle_status : int
        The last known status of the spindle (0 -> off, 2 -> CW, 3 -> CCW).
    f : int
        The current frequency value.
    line_index : int
        The current line index in the G-code.
    frequencies : List[FrequencyInformation]
        A list to store FrequencyInformation objects.
    """

    # Class variables
    last_spindle_status: int = 0  # 0 -> off, 2 -> CW, 3 -> CCW
    f: int = 0
    current_g_code_line_index: int = 0
    frequencies: List[FrequencyInformation] = []
    
    # Constructor
    def __init__(self):
        """
        Initializes the FrequencyManager instance and adds an initial FrequencyInformation object.
        """
        
        new_frequency_information = FrequencyInformation(0, 0, 0, 0, 0, 0)
        self.frequencies.append(new_frequency_information)

    #################################################################################################
    # Methods

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

        new_f = int(new_S_value / 60)     # Compute frequency in Hz

        # Check if new frequency needed
        if self.last_spindle_status != 0 and new_f != self.f:

            if self.current_g_code_line_index != g_code_line_index:
                # New frequency needed

                # End last frequency
                self.frequencies[-1].line_index_end = (g_code_line_index-1)                            

                # Make new frequency
                new_frequency_information = FrequencyInformation(line_index_start = g_code_line_index,
                                                                 line_index_end = g_code_line_index,
                                                                 expected_time_start = 0, 
                                                                 expected_duration = 0,
                                                                 frequency = new_f, 
                                                                 spindle_status = self.last_spindle_status)
                self.frequencies.append(new_frequency_information)
            else: 
                # Last frequency needs to change
                self.frequencies[-1].frequency = new_f

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

        new_spindle_status = 0

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
            self.frequencies[-1].line_index_end = (g_code_line_index-1)

            # Create new frequency information based on spindle status
            if new_spindle_status == 0:                 # spindle turns off
                new_frequency_information = FrequencyInformation(line_index_start = g_code_line_index,
                                                                 line_index_end = g_code_line_index,
                                                                 expected_time_start = 0, 
                                                                 expected_duration = 0,
                                                                 frequency = 0, 
                                                                 spindle_status = new_spindle_status)
            elif self.last_spindle_status == 0:         # spindle turns on
                new_frequency_information = FrequencyInformation(line_index_start = g_code_line_index,
                                                                 line_index_end = g_code_line_index,
                                                                 expected_time_start = 0, 
                                                                 expected_duration = 0,
                                                                 frequency = self.f, 
                                                                 spindle_status = new_spindle_status)                
            else:                                       # spindle changes direction
                new_frequency_information = FrequencyInformation(line_index_start = g_code_line_index,
                                                                 line_index_end = g_code_line_index,
                                                                 expected_time_start = 0, 
                                                                 expected_duration = 0,
                                                                 frequency = self.f, 
                                                                 spindle_status = new_spindle_status)     

            # Add new frequency information
            self.frequencies.append(new_frequency_information)

            # Update attributes
            self.last_spindle_status = new_spindle_status
            self.current_g_code_line_index = g_code_line_index

    def update(self, 
               time_stamps: List[Tuple[int, int]]) -> None:
        """
        Updates the frequency information with the expected start times and durations based on time stamps.

        Parameters:
        -----------
        time_stamps : List[Tuple[int, int]]
            A list of tuples where each tuple contains a line index and the corresponding timestamp.
        """
        time_stamp_index = 0

        for frequency in self.frequencies:
            index_start = frequency.line_index_start
            index_end = frequency.line_index_end

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

# End of class
#####################################################################################################
