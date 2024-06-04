import numpy as np
import copy

class ArcInformation:

    def __init__(self,
                 direction: int = 2,
                 I: float = 0.0,
                 J: float = 0.0,
                 K: float = 0.0,
                 radius = 0):
        
        self.direction = direction      # 2 -> CW, 3 -> CCW
        self.I = I
        self.J = J
        self.K = K
        self.radius = radius
    
    def get_arc_center_as_array(self):
        array = np.array([self.I, self.J, self.K])
        return copy.copy(array)
    
    def set_arc_center(self, arc_center):
        self.I = arc_center[0]
        self.J = arc_center[1]
        self.K = arc_center[2]
    
    def print(self):
        print(f"direction: {self.direction}; arc-center (absolut): I = {self.I}, J = {self.J}, K = {self.K}; radius: {self.radius}")