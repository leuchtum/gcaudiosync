import numpy as np

class Tool_Change_Manager:

    # counter = 0
    tool_changes = []       # index, new tool number

    def __init__(self):
        pass

    def new_Tool(self, index: int, new_tool_number: int):

        # for debugging
        # self.counter += 1
        # print("Tool_Change_Manager call no. " + str(self.counter) + ": New Tool called in line " + str(index) + ": Tool N. " + str(new_tool_number))

        self.tool_changes.append(np.array([index, new_tool_number]))