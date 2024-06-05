
class FrequencyInformation:
    """
    A class to represent frequency information for a segment of G-code.

    Attributes:
    -----------
    line_index_start : int
        The starting line index of the G-code segment.
    line_index_end : int
        The ending line index of the G-code segment.
    expected_time_start : int
        The expected start time of the segment in milliseconds.
    expected_duration : int
        The expected duration of the segment in milliseconds.
    frequency : float
        The frequency value associated with the segment.
    spindle_status : str
        The status of the spindle (0 -> off, 2 -> CW, 3 -> CCW) during the segment.
    """
   
    # Constructor
    def __init__(self, 
                 line_index_start: int, 
                 line_index_end: int, 
                 expected_time_start: int, 
                 expected_duration: int, 
                 frequency: float,
                 spindle_status: int):
    
        self.line_index_start = line_index_start
        self.line_index_end = line_index_end
        self.expected_time_start = expected_time_start
        self.expected_duration = expected_duration
        self.frequency = frequency
        self.spindle_status = spindle_status

    #################################################################################################
    # Methods

# End of class
#####################################################################################################
