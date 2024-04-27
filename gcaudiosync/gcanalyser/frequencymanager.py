class Frequancy_Manager:

    counter = 0

    def __init__(self):
        pass

    def new_S(self, index: int, new_S: int):
        self.counter += 1
        print("Frequancy_Manager call no. " + str(self.counter) + ": S changed to " + str(new_S) + " in line " + str(index))

    def new_Spindle_Operation(self, index: int, command: str):
        self.counter += 1
        print("Frequancy_Manager call no. " + str(self.counter) + ": Got new Spindle-operation in line " + str(index) + ": spindle " + command)