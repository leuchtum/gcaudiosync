
import numpy as np

from gcaudiosync.gcanalyser.frequencyinformation import FrequencyInformation

class FrequencyManager:

    #counter = 0

    last_spindle_status = 0         # 0 -> off, 3 -> CW, 4 -> CCW
    f = 0
    line_index = 0
    frequencies = []
    
    def __init__(self):
        new_frequency_information = FrequencyInformation(0, 0, 0, 0, 0, 0)
        self.frequencies.append(new_frequency_information)

    def new_S(self, line_index: int, new_S: int):
        
        new_f = int(new_S / 60)

        if self.last_spindle_status != 0 and new_f != self.f:

            if self.line_index != line_index:
                self.frequencies[-1].line_index_end = (line_index-1)
                new_frequency_information = FrequencyInformation(line_index, line_index, 0, 0, new_f, self.last_spindle_status)
                self.frequencies.append(new_frequency_information)
            else: 
                self.frequencies[-1].frequency = new_f

        self.f = new_f
        self.line_index = line_index

    def new_Spindle_Operation(self, line_index: int, command: str):

        match command:
            case "off":
                new_spindle_status = 0
            case "CW":
                new_spindle_status = 3
            case "CCW":
                new_spindle_status = 4

        if self.last_spindle_status != new_spindle_status:

            self.frequencies[-1].line_index_end = (line_index-1)

            if new_spindle_status == 0:                 # spindle turns off
                new_frequency_information = FrequencyInformation(line_index, line_index, 0, 0, 0, new_spindle_status)
            elif self.last_spindle_status == 0:         # spindle turns on
                new_frequency_information = FrequencyInformation(line_index, line_index, 0, 0, self.f, new_spindle_status)
            else:                                       # spindle changes direction
                new_frequency_information = FrequencyInformation(line_index, line_index, 0, 0, self.f, new_spindle_status)

            self.frequencies.append(new_frequency_information)
            self.last_spindle_status = new_spindle_status
            self.line_index = line_index

    def update(self, time_stamps: list):
        time_stamp_index = 0

        for frequence in self.frequencies:
            index_start = frequence.line_index_start
            index_end = frequence.line_index_end

            for index in range(time_stamp_index, len(time_stamps)):
                if time_stamps[index][0] >= index_start:
                    time_stamp_index = index
                    break
            
            frequence.expected_time_start = time_stamps[time_stamp_index][1]

            for index in range(time_stamp_index, len(time_stamps)):
                if time_stamps[index][0] >= index_end:
                    time_stamp_index = index
                    break
            
            frequence.expected_duration = time_stamps[time_stamp_index][1] - frequence.expected_time_start
            