import numpy as np

class CoolingManager:

    # counter = 0
    cooling = [np.array([0, 0, 0])]        # index_start, index_end, cooling_on

    def __init__(self):
        pass

    def new_cooling_operation(self, index: int, operation: str):

        # for debugging
        # self.counter += 1
        # print("Cooling_Manager call no. " +  str(self.counter) + ": New cooling operation was called in line " + str(index) + ": " + operation)

        if operation == "on":
            cooling_on = True
        else:
            cooling_on = False        

        if self.cooling[-1][2] != cooling_on:

            self.cooling[-1][2] = index-1
            new_cooling = np.array([index, index, cooling_on])
            self.cooling.append(new_cooling)
            