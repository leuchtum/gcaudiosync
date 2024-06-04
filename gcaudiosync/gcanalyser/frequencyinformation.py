import numpy as np

class FrequencyInformation:

    def __init__(self, 
                 line_index_start, 
                 line_index_end, 
                 expected_time_start, 
                 expected_duration, 
                 frequency,
                 spindle_status):
        self.line_index_start = line_index_start
        self.line_index_end = line_index_end
        self.expected_time_start = expected_time_start
        self.expected_duration = expected_duration
        self.frequency = frequency
        self.spindle_status = spindle_status
