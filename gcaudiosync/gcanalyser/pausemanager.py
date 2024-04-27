class Pause_Manager:

    counter = 0

    def __init__(self):
        pass

    def new_dwell(self, index:int, time:int):
        self.counter += 1
        print("Pause_Manager call no. " + str(self.counter) + ": Dewll was added in line " + str(index) + ": " + str(time) + " ms")

    def new_pause(self, index:int, kind_of_pause: int):
        self.counter += 1
        print("Pause_Manager call no. " + str(self.counter) + ": Pause " + str(kind_of_pause) + " was added in in line " + str(index))
    