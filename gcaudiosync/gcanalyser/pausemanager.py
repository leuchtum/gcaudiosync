import numpy as np

class Pause_Manager:

    # counter = 0

    pauses = []         # index, kind of pause (0: abort, 1: quit, 2: PROGABORT, 4: dwell - G04), expexted_start_time [ms], expected time [ms] (-1 = unknown)

    def __init__(self):
        pass

    def new_dwell(self, index:int, time:int):

        # for debugging
        # self.counter += 1
        # print("Pause_Manager call no. " + str(self.counter) + ": Dewll was added in line " + str(index) + ": " + str(time) + " ms")

        self.pauses.append(np.array([index, 4, 0, time]))

    def new_pause(self, index:int, kind_of_pause: int):

        # for debuging
        # self.counter += 1
        # print("Pause_Manager call no. " + str(self.counter) + ": Pause " + str(kind_of_pause) + " was added in in line " + str(index))

        # here it might be good to inform the frequancy manager that the spindle could stand still. not implemented jet
        # or frequency-manager looks over all pauses at the end.

        self.pauses.append(np.array([index, kind_of_pause, 0, -1]))

    def update(self, time_stamps):
        for pause in self.pauses:
            time_stamp_index = 0
            pause_index = pause[0]

            for index in range(time_stamp_index, len(time_stamps)):
                if time_stamps[index][0] >= pause_index:
                    time_stamp_index = index
                    break

            pause[2] = time_stamps[time_stamp_index][1]