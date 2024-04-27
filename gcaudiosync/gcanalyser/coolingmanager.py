class Cooling_Manager:

    counter = 0

    def __init__(self):
        pass

    def new_cooling_operation(self, index: int, operation: str):
        self.counter += 1
        print("Cooling_Manager call no. " +  str(self.counter) + ": New cooling operation was called in line " + str(index) + ": " + operation)