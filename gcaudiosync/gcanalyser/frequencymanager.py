
import numpy as np

class Frequency_Manager:

    #counter = 0

    last_spindle_status = 0         # 0 -> off, 3 -> CW, 4 -> CCW
    f = 50                          # default: 50 Hz (3000 RPM)
    index = 0
    frequencies = [np.array([0, 0, 0, 0, 0])]  # index_start, index_end, expected duration [ms], frequency [Hz], spindle_status
    
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
                new_info = np.array([index, index, 0, new_f, self.last_spindle_status])
                self.frequencies.append(new_info)
            else: 
                self.frequencies[-1][3] = new_f

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
                new_info = np.array([index, index, 0, 0, new_spindle_status])
            elif self.last_spindle_status == 0:         # spindle turns on
                new_info = np.array([index, index, 0, self.f, new_spindle_status])
            else:                                       # spindle changes direction
                new_info = np.array([index, index, 0, self.f, new_spindle_status])

            self.frequencies.append(new_info)
            self.last_spindle_status = new_spindle_status
            self.index = index
