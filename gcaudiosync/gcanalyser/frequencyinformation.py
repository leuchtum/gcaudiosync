
class FrequencyInformation:
    """
    A class to represent frequency information for a segment of G-code.

    Attributes:
    -----------
    g_code_line_index_start : int
        The starting line index of the G-code segment.
    g_code_line_index_end : int
        The ending line index of the G-code segment.
    expected_time_start : int
        The expected start time of the segment in milliseconds.
    expected_duration : int
        The expected duration of the segment in milliseconds.
    frequency : int
        The frequency value associated with the segment.
    spindle_status : int
        The status of the spindle (0 -> off, 2 -> CW, 3 -> CCW) during the segment.
    """
   
    # Constructor
    def __init__(self, 
                 g_code_line_index_start: int, 
                 g_code_line_index_end: int, 
                 frequency: int,
                 spindle_status: int):
        """
        Initializes the FrequencyInformation object.

        Parameters:
        -----------
        g_code_line_index_start : int
            Index of the g-code line where the frequence starts.
        g_code_line_index_end: int
            Index of the g-code line where the frequence ends.
        frequency: int
            Frequency in Hz
        spindle_status: int
            Status of spindle. 0: off, 2: CW, 3: CCW

        """

        # Create Attributes and save the Parameters
        self.g_code_line_index_start = g_code_line_index_start
        self.g_code_line_index_end = g_code_line_index_end
        self.expected_time_start: float = 0.0
        self.expected_duration: float = 0.0
        self.frequency = frequency
        self.spindle_status = spindle_status

    #################################################################################################
    # Methods
    def print_info(self) -> None:
        """
        Prints all info of the frequency information
        """
        print(f"    Start of frequency: G-Code line index {self.g_code_line_index_start}")
        print(f"    End of frequency: G-Code line index {self.g_code_line_index_end}")
        print(f"    Frequence: {self.frequency} Hz")

# End of class
#####################################################################################################
