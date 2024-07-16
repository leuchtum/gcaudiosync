
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
                 expected_time_start: int, 
                 expected_duration: int, 
                 frequency: int,
                 spindle_status: int):
    
        self.g_code_line_index_start = g_code_line_index_start
        self.g_code_line_index_end = g_code_line_index_end
        self.expected_time_start = expected_time_start
        self.expected_duration = expected_duration
        self.frequency = frequency
        self.spindle_status = spindle_status

    #################################################################################################
    # Methods
    def info(self) -> None:
        print(f"Start of frequency: G-Code line index {self.g_code_line_index_start}")
        print(f"End of frequency: G-Code line index {self.g_code_line_index_end}")
        print(f"frequence: {self.frequency} Hz")

# End of class
#####################################################################################################
