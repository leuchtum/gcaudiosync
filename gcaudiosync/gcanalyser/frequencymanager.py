
import numpy as np

class Frequency_Manager:

    #counter = 0

    last_spindle_status = 0         # 0 -> off, 3 -> CW, 4 -> CCW
    f = 50                          # default: 50 Hz (3000 RPM)
    index = 0
    frequencies = [np.array([0, 0, 0, 0, 0])]  # index_start, index_end, expexted_start_time [ms], expected duration [ms], frequency [Hz], spindle_status
    
    def __init__(self):
        pass

    def new_S(self, index: int, new_S: int):
        
        # for debugging
        # self.counter += 1
        # print("Frequancy_Manager call no. " + str(self.counter) + ": S changed to " + str(new_S) + " in line " + str(index))
        new_f = int(new_S / 60)

        if self.last_spindle_status != 0 and new_f != self.f:

            if self.index != index:
                self.frequencies[-1][1] = (index-1)
                new_info = np.array([index, index, 0, 0, new_f, self.last_spindle_status])
                self.frequencies.append(new_info)
            else: 
                self.frequencies[-1][4] = new_f

        self.f = new_f
        self.index = index

    def new_Spindle_Operation(self, index: int, command: str):

        # for debugging
        #self.counter += 1
        #print("Frequancy_Manager call no. " + str(self.counter) + ": Got new Spindle-operation in line " + str(index) + ": spindle " + command)

        match command:
            case "off":
                new_spindle_status = 0
            case "CW":
                new_spindle_status = 3
            case "CCW":
                new_spindle_status = 4

        if self.last_spindle_status != new_spindle_status:

            self.frequencies[-1][1] = (index-1)

            if new_spindle_status == 0:                 # spindle turns off
                new_info = np.array([index, index, 0, 0, 0, new_spindle_status])
            elif self.last_spindle_status == 0:         # spindle turns on
                new_info = np.array([index, index, 0, 0, self.f, new_spindle_status])
            else:                                       # spindle changes direction
                new_info = np.array([index, index, 0, 0, self.f, new_spindle_status])

            self.frequencies.append(new_info)
            self.last_spindle_status = new_spindle_status
            self.index = index

    def update(self, time_stamps: list):
        time_stamp_index = 0

        for frequence in self.frequencies:
            index_start = frequence[0]
            index_end = frequence[1]

            for index in range(time_stamp_index, len(time_stamps)):
                if time_stamps[index][0] >= index_start:
                    time_stamp_index = index
                    break
            
            frequence[2] = time_stamps[time_stamp_index][1]

            for index in range(time_stamp_index, len(time_stamps)):
                if time_stamps[index][0] >= index_end:
                    time_stamp_index = index
                    break
            
            frequence[3] = time_stamps[time_stamp_index][1] - frequence[2]
            