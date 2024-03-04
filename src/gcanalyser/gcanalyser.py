import numpy as np
import pandas as pd

from typing import Union

class GCodeAnalyser:

    # Constructor
    def __init__(self):
        pass

    def analyse(self, g_code_src) -> None: #TODO
        '''
        Analyse a g-code for a CNC-machine (milling)

        Args:
            g_code_src:     global path to the g-code-file
            CNC_Machine:    CNC-machine-object with all data of the CNC-machine

        Returns:
            None
        '''

        # read in the g_code
        g_code = read_cnc_file(g_code_src)  

        print(g_code)

        # end of class
######################################################################################################
# functions
  
def read_cnc_file(src_path: str) -> Union[list[str], int]:
    """
    Reads a G-code file and returns its contents or an error code.

    Args:
        src_path: Absolute path to the file.

    Returns:
        - list of strings: Each string represents a line from the file, including an additional empty line at the beginning, on successful read.
        - int: 1 if FileNotFoundError occurs, 2 for other errors.
    """

    try:
        with open(src_path) as file:
            return ["\n"] + file.readlines()
    except FileNotFoundError:
        print("File not found")
        return 1
    except Exception as e:  # Catch all other exceptions
        print(f"An error occurred while reading the file: {e}")
        return 2