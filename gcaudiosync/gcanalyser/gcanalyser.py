import math

import numpy as np
import pandas as pd

from typing import Union, Any
from gcaudiosync.gcanalyser.cncparameter import CNC_Parameter

class GCodeAnalyser:    

    # list with the column names and the datatypes for the visualization data
    Col_Names_and_DataTypes_visualization = np.dtype(
        [
            ("original_line_content",   str),           # original line of the cgode
            ("important",               np.bool_),      # bool if line is important for synchronisation, filles out by interpreter
            ("time",                    np.uint64),     # time this line needs in ms
            ("index_all",               np.uint64),     # start of this data in all data
        ]
    )

    # list with the column names and the datatypes for the intern data
    Col_Names_and_DataTypes_intern = np.dtype(
        [
            ("important",           np.bool_),          # bool if line is important for synchronisation, filles out by interpreter
            ("N",                   np.int64),          # line number -> copied out of the original line if possible, filled out by parser
            ("movement",            np.uint8),          # movement (0, 1, 2, 3), filled out by parser
            ("has_movement",        np.bool_),          # True if line has movement
            ("X",                   np.float64),        # value of X-coordinate, filled out by parser, corrected by interpreter
            ("Y",                   np.float64),        # value of Y-coordinate, filled out by parser, corrected by interpreter
            ("Z",                   np.float64),        # value of Z-coordinate, filled out by parser, corrected by interpreter
            ("A",                   np.float64),        # value of A-coordinate, filled out by parser, corrected by interpreter
            ("B",                   np.float64),        # value of B-coordinate, filled out by parser, corrected by interpreter
            ("C",                   np.float64),        # value of C-coordinate, filled out by parser, corrected by interpreter
            ("I",                   np.float64),        # value of I-coordinate, filled out by parser, corrected by interpreter
            ("J",                   np.float64),        # value of J-coordinate, filled out by parser, corrected by interpreter
            ("K",                   np.float64),        # value of K-coordinate, filled out by parser, corrected by interpreter
            ("arc_radius",          np.float64),        # value of arc radius, filled out by parser, corrected by interpreter
            ("arc_full_turns",      np.uint64),         # number of full turns in a G02 or G03 move, filled out by parser
            ("R",                   np.float64),        # value of R-value, filled out by parser
            ("P",                   np.float64),        # value of P-value, filled out by parser
            ("F",                   np.float64),        # feed rate for G01, G02 and G03 -> important for tracking F, filled out by parser
            ("feed_rate",           np.float64),        # actual feed rate in this line [mm/min] -> important for synchronisation, filled out by interpreter
            ("S",                   np.float64),        # spindle speed if the spindle is on -> important for tracking S, filled out by parser
            ("spindle_speed",       np.float64),        # actual spindle speed in this line [RPM] -> important for synchronisation, filled out by interpreter
            ("spindle_speed_change",np.bool_),          # True if previous line has diffrend spindle speed
            ("dwell_time",          np.uint64),         # value of dwell time in ms   
            ("exact_stop",          np.bool_),          # exact stop
            ("G_61_on",             np.bool_),          # True if G61 is on
            ("active_plane",        np.uint8),          # active plane 
            ("cutter_compensation", np.float64),        # kind of cutter compensation
            ("absolute_position",   np.bool_),          # True if position are absolute
            ("absolute_arc_center", np.bool_),          # True if arc center position is absolute
            ("program_paused",      np.bool_),          # True if program is paused in this line     
            ("spindle_on",          np.bool_),          # is spindle on or not
            ("spindle_direction",   str),               # direction of spindle
            ("active_tool_number",  np.uint8),          # number of active tool
            ("tool_diameter",       np.float64),        # diameter of tool
            ("tool_length",         np.float64),        # diameter of tool
            ("tool_change",         np.bool_),          # True if tool change
            ("cooling_on",          np.bool_),          # True if cooling ist on
            ("cooling_change",      np.bool_),          # True if cooling changes
            ("program_end_reached", np.bool_),          # True if program end reached
        ]
    )

    # list with the column names and the datatypes for the all the data for synchronisation
    Col_Names_and_DataTypes_all = np.dtype(
        [   
            ("what_happens",        np.uint8),          # 0: start of program
                                                        # 1: linear movement
                                                        # 2: arc movement
                                                        # 3: end of program
                                                        # 4: pause
                                                        # 5: dwell time
                                                        # 6: tool change
                                                        # 7: cooling change
                                                        # 8: RPM change
                                                    
            ("index_visualisation", np.uint64),         # index for same line in visualisation data
            ("movement",            np.uint8),          # movement (0, 1, 2, 3), filled out by parser
            ("X",                   np.float64),        # value of X-coordinate, filled out by parser, corrected by interpreter
            ("Y",                   np.float64),        # value of Y-coordinate, filled out by parser, corrected by interpreter
            ("Z",                   np.float64),        # value of Z-coordinate, filled out by parser, corrected by interpreter
            ("A",                   np.float64),        # value of A-coordinate, filled out by parser, corrected by interpreter
            ("B",                   np.float64),        # value of B-coordinate, filled out by parser, corrected by interpreter
            ("C",                   np.float64),        # value of C-coordinate, filled out by parser, corrected by interpreter
            ("I",                   np.float64),        # value of I-coordinate, filled out by parser, corrected by interpreter
            ("J",                   np.float64),        # value of J-coordinate, filled out by parser, corrected by interpreter
            ("K",                   np.float64),        # value of K-coordinate, filled out by parser, corrected by interpreter
            ("arc_radius",          np.float64),        # value of arc radius, filled out by parser, corrected by interpreter
            ("arc_full_turns",      np.uint64),         # number of full turns in a G02 or G03 move, filled out by parser
            ("feed_rate",           np.float64),        # actual feed rate in this line [mm/min] -> important for synchronisation, filled out by interpreter
            ("spindle_speed",       np.float64),        # actual spindle speed in this line [RPM] -> important for synchronisation, filled out by interpreter
            ("spindle_speed_change",np.bool_),          # True if previous line has diffrend spindle speed            
            ("dwell_time",          np.uint64),         # value of dwell time in ms   
            ("active_plane",        np.uint8),          # active plane 
            ("program_paused",      np.bool_),          # true if program is paused in this line     
            ("spindle_on",          np.bool_),          # is spindle on or not
            ("spindle_direction",   str),               # direction of spindle
            ("exact_stop",          np.bool_),          # exact stop
            ("active_tool_number",  np.uint8),          # number of active tool
            ("tool_diameter",       np.float64),        # diameter of tool
            ("tool_length",         np.float64),        # diameter of tool
            ("tool_change",         np.bool_),          # True if tool change
            ("cooling_on",          np.bool_),          # True if cooling ist on
            ("cooling_change",      np.bool_),          # True if cooling changes
            ("program_end_reached", np.bool_),          # True if program end reached
            ("time",                np.int64)           # time in ms
        ]
    )

    # Constructor
    def __init__(self):
        self.CNC_Parameter = CNC_Parameter()

    ##################################################################################################
    # Methods: "Analyser"
    # TODO
    def analyse(self, g_code_src) -> None:
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

        # create two empty DataFrames: 
            # one with the column names and data types defined previously for intern data
            # one with the original line and the time it will need
        self.Data_intern = pd.DataFrame(np.empty(len(g_code), dtype = self.Col_Names_and_DataTypes_intern))
        self.Data_visualisation = pd.DataFrame(np.empty(len(g_code), dtype = self.Col_Names_and_DataTypes_visualization))

        # prepare first index of intern data
        self.prepare_first_index()

        # parse every line in g-code
        for index in range(len(g_code)):
            self.g_code_line_parser(g_code[index], index)

        # interpret g-code and fill dataframe
        self.interprete()

    ##################################################################################################
    # Methods: Interact with DataFrame
        
    def get_from_intern_data(self, index: int, column: str) -> Any:
        """
        Retrieves a value from the specified index and column in the Data_intern.

        Args:
            index (int):    The index of the row to access.
            column (str):   The name of the column to access.

        Returns:
            Any: The value at the specified location in the Data_intern, or raises a KeyError if the index or column is not found.

        Raises:
            KeyError: If the specified index or column is not found in the Data_intern.
        """

        try:
            return self.Data_intern.loc[index, column]
        except KeyError:
            raise KeyError(f"Index {index} or column '{column}' not found in Data_intern")
 
    def write_in_intern_data(self, index: int, column: str, data) -> None:
        """
        Inserts or updates a value in the specified cell of the Data_intern.

        Args:
            index (int):    The index of the row to modify.
            column (str):   The name of the column to modify.
            data:           The new value to insert or update.

        Returns:
            None
        """

        self.Data_intern.loc[index, column] = data
        
    def get_from_visualization_data(self, index: int, column: str) -> Any:
        """
        Retrieves a value from the specified index and column in the Data_visualisation.

        Args:
            index (int):    The index of the row to access.
            column (str):   The name of the column to access.

        Returns:
            Any: The value at the specified location in the Data_visualisation, or raises a KeyError if the index or column is not found.

        Raises:
            KeyError: If the specified index or column is not found in the Data_visualisation.
        """

        try:
            return self.Data_visualisation.loc[index, column]
        except KeyError:
            raise KeyError(f"Index {index} or column '{column}' not found in Data_visualisation")
 
    def write_in_visualization_data(self, index: int, column: str, data) -> None:
        """
        Inserts or updates a value in the specified cell of the Data_visualisation.

        Args:
            index (int):    The index of the row to modify.
            column (str):   The name of the column to modify.
            data:           The new value to insert or update.

        Returns:
            None
        """

        self.Data_visualisation.loc[index, column] = data

    def get_from_all_data(self, index: int, column: str) -> Any:
        """
        Retrieves a value from the specified index and column in the Data_all.

        Args:
            index (int):    The index of the row to access.
            column (str):   The name of the column to access.

        Returns:
            Any: The value at the specified location in the Data_intern, or raises a KeyError if the index or column is not found.

        Raises:
            KeyError: If the specified index or column is not found in the Data_intern.
        """

        try:
            return self.Data_all.loc[index, column]
        except KeyError:
            raise KeyError(f"Index {index} or column '{column}' not found in Data_all")
 
    def write_in_all_data(self, index: int, column: str, data) -> None:
        """
        Inserts or updates a value in the specified cell of the Data_all.

        Args:
            index (int):    The index of the row to modify.
            column (str):   The name of the column to modify.
            data:           The new value to insert or update.

        Returns:
            None
        """

        self.Data_all.loc[index, column] = data

    def copy_all_from_line_above_intern_data(self, index: int) -> None:
        """
        Copies data from the line above a given index in the internal DataFrame.

        Args:
            self: Reference to the object itself (usually 'self').
            index: The index of the row to copy data into.

        Returns:
            None
        """

        # Check if the index is within bounds
        if index <= 0:
            raise ValueError("Index cannot be less than or equal to 0")

        # Useiloc for efficient single row retrieval and copy
        self.Data_intern.loc[index] = self.Data_intern.iloc[index-1].copy()

    def copy_from_line_above_intern_data(self, index: int, columns: list[str]) -> None:
        """
        Copies values from columns in the previous line to the current line.

        Args:
            index (int):            The index of the current line.
            columns (list[str]):    A list of column names to copy the values from.

        Returns:
            None
        """

        if index >= 1:
            for column in columns:
                value = self.get_from_intern_data(index - 1, column)
                self.write_in_intern_data(index, column, value)
                
    #TODO: fill in if DataFrame extends
    def prepare_first_index(self) -> None:          
        '''
        Prepares first index of the Dataframe with data. All other columns are False or 0.

        Args:
            None
        
        Returns:
            None
        '''

        self.write_in_intern_data(0, "important", True)                                 # first line is important
        self.write_in_intern_data(0, "movement", 0)                                     # start movement: G00
        self.write_in_intern_data(0, "X", self.CNC_Parameter.tool_change_point[0])      # start X-coordinate: Tool change point of CNC-machine
        self.write_in_intern_data(0, "Y", self.CNC_Parameter.tool_change_point[1])      # start Y-coordinate: Tool change point of CNC-machine
        self.write_in_intern_data(0, "Z", self.CNC_Parameter.tool_change_point[2])      # start Z-coordinate: Tool change point of CNC-machine
        self.write_in_intern_data(0, "A", 0.0)                                          # start A-coordinate: Tool change point of CNC-machine
        self.write_in_intern_data(0, "B", 0.0)                                          # start B-coordinate: Tool change point of CNC-machine
        self.write_in_intern_data(0, "C", 0.0)                                          # start C-coordinate: Tool change point of CNC-machine
        self.write_in_intern_data(0, "cutter_compensation", 40)                         # cutter compensation off
        self.write_in_intern_data(0, "absolute_position", True)                         # positions are given in absolute values
        self.write_in_intern_data(0, "active_plane", 17)                                # active plane is XY-plane

    ##################################################################################################
    # Methods: Parser
        
    def g_code_line_parser(self, g_code_line: str, index: int) -> None:
        """
        Parse a G-code line, extract relevant information, and write it to the Data_intern and Data_visualisation.

        Args:
            index (int):        The index of the row to write the parsed data to.
            g_code_line (str):  The raw G-code line to parse.

        Returns:
            None
        """

        self.write_in_visualization_data(index, "original_line_content", g_code_line.strip('\n'))   # write original code into DataFrame


        # copy tool data from line above
        columns = [
                    "active_tool_number",
                    "tool_diameter",
                    "tool_length",
                   ]
        self.copy_from_line_above_intern_data(index, columns)                                     

        g_code_line = prepare_line(g_code_line)                                 # remove useless info from line
        
        g_code_line = self.handle_line_number(g_code_line, index)               # handle line number

        g_code_line = self.handle_g(g_code_line, index)                         # handle all the Gs

        g_code_line = self.handle_m(g_code_line, index)                         # handle all the Ms

        # copy S and F data from line above
        columns = [
            "F",
            "S",
        ]
        self.copy_from_line_above_intern_data(index, columns)
        
        g_code_line = self.handle_f(g_code_line, index)                         # handle F
        g_code_line = self.handle_s(g_code_line, index)                         # handle S

        # print what is left
        if g_code_line != "":
            print(f"Line {index} was not parsed completely. Unparsed content: " + g_code_line)

    def handle_line_number(self, line: str, index: int) -> str:
        """
            Extracts and validates line number from the given line, writes it to DataFrame, and returns the line with the line number removed.

            Args:
                line (str):     The G-code line to process.
                index (int):    The index of the current line in the DataFrame.

            Returns:
                line: The modified G-code line with the line number removed.
        """
        
        # get N 
        line, available, N = get_number(line, "N", True)
        N = int(N)
        
        # write N into the DataFrame
        if not available:
            N = 0
        self.write_in_intern_data(index, "N", int(N))

        return line                             
        
    def handle_g(self, line: str, index: int) -> str:
        '''
        Handle G-codes in a given line of the G-code.

        Args:
            line (str):     The line of G-code to handle.
            index (int):    The index of the line in the G-code file.

        Returns:
            line (str):     The modified G-code line.
        '''

        # Copy given G-codes from above if this is not the first line
        columns = [
            "movement",
            "X",
            "Y",
            "Z",
            "A",
            "B",
            "C",
            "I",
            "J",
            "K",
            "arc_radius",
            "absolute_position", 
            "absolute_arc_center", 
            "active_plane",
            "cutter_compensation",
        ]

        if self.get_from_intern_data(index, "G_61_on"):
            columns.append("exact_stop")

        self.copy_from_line_above_intern_data(index, columns)

        movement_available = False
        movement_possible = True

        # Extract numbers from the G-code line
        line, numbers = get_numbers(line, "G", True)

        # Iterate over each G-code number in the line
        for number_index in range(len(numbers)):
            number = float(numbers[number_index])

            # Handle different G-codes using a match statement
            match number:
                case 0 | 1:     # Rapid linear movement, Linear movement
                    movement_available = True
                    self.write_in_intern_data(index, "movement", int(number))
                    line = self.handle_linear_movement(line, index)
                case 2 | 3:     # Arc movement CW, Arc movement CCW
                    movement_available = True
                    self.write_in_intern_data(index, "movement", int(number))
                    line = self.handle_arc_movement(line, index)
                case 4:     # Dwell
                    movement_possible = False
                    line = self.handle_g04(line, index) 
                case 9:     # Exact stop
                    self.handle_exact_stop(index)
                case 17 | 18 | 19:    # Select XY-plane, Select XZ-plane, Select YZ-plane
                    self.handle_plane_selection(index, number)
                case 20:    # Inch
                    raise Exception("Please use metric system, imperial system is not supported.")
                case 21:    # mm
                    pass    # Standard unit, nothing to do
                case 40 | 41 | 41.1 | 42 | 42.1:    # Cutter compensation
                    line = self.handle_cutter_compensation(line, index, number)
                case 61:    # exact stop on for this and following lines
                    self.handle_g_61_on(index)
                case 64:    # exact stop off
                    self.handle_g_61_off(index)
                case 90 | 90.1 | 91 | 91.1:    # Absolute position
                    self.handle_value_command(index, number)
                case _:  # Unsupported G-code
                    print(f"G{number} found in line {index}. No action defined in method (handle_G)")

        # Check if coordinates without movement
        if not movement_available and index != 0 and movement_possible:
            number = self.get_from_intern_data(index, "movement")
            if number in [0, 1]:
                line = self.handle_linear_movement(line, index)
            else:
                line = self.handle_arc_movement(line, index)

        return line

    def handle_linear_movement(self, line: str, index: int) -> str:
        '''
        Handle linear movement coordinates in a given line of the G-code.

        Args:
            line (str):     The line of G-code to handle.
            index (int):    The index of the line in the G-code file.

        Returns:
            line (str):     The modified G-code line.
        '''

        line_has_movement = False  # Flag to track if movement coordinates are present in the line

        coordinates = ["X", "Y", "Z", "A", "B", "C"]  # List of supported movement coordinates

        for coordinate in coordinates:
            line, available, value = get_number(line, coordinate, True)  # Extract coordinate value from the line

            value = float(value)  # Convert coordinate value to float

            if available:  # Check if coordinate is available in the line
                if not self.get_from_intern_data(index, "absolute_position"):
                    # Update coordinate value based on absolute/relative positioning
                    value = self.get_from_intern_data(index, coordinate) + value

                # Write the updated coordinate value into the internal data
                self.write_in_intern_data(index, coordinate, value)

                line_has_movement = True  # Set flag to True indicating movement coordinates are present

        if line_has_movement:
            # Mark the line as important if movement coordinates are present
            self.write_in_intern_data(index, "has_movement", True)
            self.write_in_intern_data(index, "important", True)
            self.write_in_visualization_data(index, "important", True)

        return line

    #TODO: make methods or functions
    def handle_arc_movement(self, line: str, index: int) -> str:
        '''
        Handle arc movement coordinates in a given line of the G-code.

        Args:
            line (str):     The line of G-code to handle.
            index (int):    The index of the line in the G-code file.

        Returns:
            line (str):     The modified G-code line.
        '''
        line_has_movement = False  # Flag to track if movement coordinates are present in the line
     
        format = 0  # Initialize format to 0

        # Define supported coordinate sets based on arc movement formats
        coordinates_0 = ["X", "Y", "Z", "A", "B", "C"]
        coordinates_1 = ["I", "J", "K"]
        coordinates_2 = ["R"]
        coordinates_3_4 = ["P"]

        coordinates = []  # Initialize list to hold coordinates based on arc movement format

        # Determine the format of the arc movement and populate the coordinates list accordingly
        if any(coordinate in line for coordinate in coordinates_1):
            format = 1
            coordinates = coordinates_0 + coordinates_1
        elif any(coordinate in line for coordinate in coordinates_2):
            format = 2
            coordinates = coordinates_0 + coordinates_2

        if any(coordinate in line for coordinate in coordinates_3_4):
            format += 2
            coordinates = coordinates + coordinates_3_4
        
        # Iterate over each coordinate in the line
        for coordinate in coordinates:

            line, available, value = get_number(line, coordinate, True)
            value = float(value)

            if available:  # Check if coordinate is available in the line
                    if coordinate in coordinates_0:
                        # Update coordinate value based on absolute/relative positioning
                        if not self.get_from_intern_data(index, "absolute_position"):    
                            value = self.get_from_intern_data(index, coordinate) + value
                        self.write_in_intern_data(index, coordinate, value)  # Write value of coordinate in line
                    elif coordinate in coordinates_1:
                        # Update coordinate value based on absolute/relative arc center
                        if not self.get_from_intern_data(index, "absolute_arc_center"):
                            value = self.get_from_intern_data(index, coordinate) + value
                        self.write_in_intern_data(index, coordinate, value)
                    elif coordinate in coordinates_2:
                        # Write the arc radius into the internal data
                        self.write_in_intern_data(index, "arc_radius", value)
                    elif coordinate in coordinates_3_4:
                        # Write the full circle turns into the internal data
                        self.write_in_intern_data(index, "arc_full_turns", int(value))

                    line_has_movement = True  # Set flag to True indicating movement coordinates are present
  
        if line_has_movement:
            # Mark the line as important if movement coordinates are present
            self.write_in_intern_data(index, "has_movement", True)
            self.write_in_intern_data(index, "important", True)
            self.write_in_visualization_data(index, "important", True)

        #TODO: make methods or functions
        if format in [1, 3]:
            match self.get_from_intern_data(index, "active_plane"):
                case 17:
                    X = self.get_from_intern_data(index, "X")
                    Y = self.get_from_intern_data(index, "Y")
                    I = self.get_from_intern_data(index, "I")
                    J = self.get_from_intern_data(index, "J")

                    DXI = abs(X-I)
                    DYJ = abs(Y-J)

                    arc_radius = math.sqrt(math.pow(DXI, 2) + math.pow(DYJ, 2))

                    self.write_in_intern_data(index, "K", 0)
                    self.write_in_intern_data(index, "arc_radius", arc_radius)

                case 18:
                    X = self.get_from_intern_data(index, "X")
                    Z = self.get_from_intern_data(index, "Z")
                    I = self.get_from_intern_data(index, "I")
                    K = self.get_from_intern_data(index, "K")

                    DXI = abs(X-I)
                    DZK = abs(Z-K)

                    arc_radius = math.sqrt(math.pow(DXI, 2) + math.pow(DZK, 2))

                    self.write_in_intern_data(index, "J", 0)
                    self.write_in_intern_data(index, "arc_radius", arc_radius)

                case 19:
                    Y = self.get_from_intern_data(index, "Y")
                    Z = self.get_from_intern_data(index, "Z")
                    J = self.get_from_intern_data(index, "J")
                    K = self.get_from_intern_data(index, "K")

                    DYJ = abs(Y-J)
                    DZK = abs(Z-K)

                    arc_radius = math.sqrt(math.pow(DYJ, 2) + math.pow(DZK, 2))

                    self.write_in_intern_data(index, "I", 0)
                    self.write_in_intern_data(index, "arc_radius", arc_radius)
                case _:
                    raise Exception("Fatal Error in line " + str(index))
        
        elif format in [2, 4]:
            match self.get_from_intern_data(index, "active_plane"):
                case 17:
                    axis_1 = "X"
                    axis_2 = "Y"
                    CX, CY = self.compute_arc_center(index, axis_1, axis_2)
                    self.write_in_intern_data(index, "I", CX)
                    self.write_in_intern_data(index, "J", CY)
                    self.write_in_intern_data(index, "K", 0)
                case 18:
                    axis_1 = "Z"
                    axis_2 = "X"
                    CZ, CX = self.compute_arc_center(index, axis_1, axis_2)
                    self.write_in_intern_data(index, "I", CX)
                    self.write_in_intern_data(index, "J", 0)
                    self.write_in_intern_data(index, "K", CZ)        
                case 19:
                    axis_1 = "Y"
                    axis_2 = "Z"
                    CX, CY = self.compute_arc_center(index, axis_1, axis_2)
                    self.write_in_intern_data(index, "I", 0)
                    self.write_in_intern_data(index, "J", CX)
                    self.write_in_intern_data(index, "K", CY)
                case _:   # Unsupported plane
                    raise Exception("Fatal Error in line " + str(index))
       
        return line

    def compute_arc_center(self, index: int, axis_1: str, axis_2: str) -> tuple[float, float]:        
        '''
        Compute the center of an arc based on the provided axis coordinates.

        Args:
            index (int): The index of the current line in the G-code file.
            axis_1 (str): The first axis coordinate (e.g., "X", "Y", or "Z").
            axis_2 (str): The second axis coordinate (e.g., "X", "Y", or "Z").

        Returns:
            Tuple containing the two coordinates of the arc center.
        '''

        arc_movement = self.get_from_intern_data(index, "movement")
        P0X = self.get_from_intern_data(index-1, axis_1)
        P0Y = self.get_from_intern_data(index-1, axis_2)
        P1X = self.get_from_intern_data(index, axis_1)
        P1Y = self.get_from_intern_data(index, axis_2)
        R = self.get_from_intern_data(index, "arc_radius")

        MX = P0X + ((P1X - P0X) / 2)
        MY = P0Y + ((P1Y - P0Y) / 2)

        P0MX = MX - P0X
        P0MY = MY - P0Y

        DP0M = math.sqrt(math.pow(P0MX,2) + math.pow(P0MY,2))

        DMC = math.sqrt(math.pow(R,2) - math.pow(DP0M,2))

        if arc_movement == 2:
            if R > 0:
                MCX = P0MY
                MCY = -P0MX
            else:
                MCX = -P0MY
                MCY = P0MX
        else:
            if R > 0:
                MCX = -P0MY
                MCY = P0MX
            else:
                MCX = P0MY
                MCY = -P0MX

        MCX = MCX / (math.sqrt(math.pow(MCX,2) + math.pow(MCY,2))) * DMC
        MCY = MCY / (math.sqrt(math.pow(MCX,2) + math.pow(MCY,2))) * DMC
        
        CX = MX + MCX
        CY = MY + MCY

        return CX, CY

    def handle_g04(self, line: str, index: int) -> str:
        '''
        Handle the G04 (dwell) command in the given line of the G-code.

        Args:
            line (str):     The line of G-code to handle.
            index (int):    The index of the line in the G-code file.

        Returns:
            line (str):     The modified G-code line.
        '''

        # Extract the dwell time from the G-code line
        line, available, number = get_number(line, "P", delete = True)

        # Check if the dwell time is available
        if not available:
            raise Exception(f"Missing dwell time in g-code line {index}")

        # Convert the dwell time to milliseconds if it's in seconds
        dwell = float(number)
        if "." in number:  # If the number contains a dot, it's in seconds
            dwell *= 1000  # Convert seconds to milliseconds
        
        # Write dwell time to internal data storage
        self.write_in_intern_data(index, "dwell_time", int(dwell))

        # Mark the line as important in internal and visualization data
        self.write_in_intern_data(index, "important", True)
        self.write_in_visualization_data(index, "important", True)

        return line

    def handle_exact_stop(self, index: int) -> None:
        '''
        Handle the command for an exact stop in a specific line of the G-code.

        Args:
            index(int):     The index of the line in the G-code file.

        Returns:
            None
        '''
        self.write_in_intern_data(index, "exact_stop", True)

    def handle_plane_selection(self, index: int, plane: int) -> None:
        '''
        Handle the selection of the active plane in the given line of the G-code.

        Args:
            index (int):    The index of the line in the G-code file.
            plane (int):    The code representing the selected plane.

        Returns:
            None
        '''  
        
        # Write the selected plane to internal data storage
        self.write_in_intern_data(index, "active_plane", plane)

    def handle_cutter_compensation(self, line: str, index: int, cutter_compensation: float) -> str:
        '''
        Handle the cutter compensation command in the given line of the G-code.

        Args:
            line (str):                     The line of G-code to handle.
            index (int):                    The index of the line in the G-code file.
            cutter_compensation (float):    The type of cutter compensation.

        Returns:
            line (str):                     The modified line after handling the cutter compensation command.
        '''

        # Write the cutter compensation type to internal data storage 
        self.write_in_intern_data(index, "cutter_compensation", cutter_compensation)

        # If cutter compensation requires diameter, extract it from the line
        if cutter_compensation in [41.1, 42.1]:
            line, found_D, diameter = get_number(line, "D", delete = True)
            diameter = float(diameter)

            # Check if the diameter is found
            if found_D:
                self.write_in_intern_data(index, "tool_diamter", diameter)
            else:
                raise Exception(f"Error in g-code line {index}: Cutter compensation .1 without Diameter called")
        
        return line

    def handle_g_61_on(self, index: int) -> None:
        '''
        Activates G61

        Args:
            index (int):    The index of the line in the G-code file.

        Returns:
            None
        '''
        self.write_in_intern_data(index, "G_61_on", True)
        self.write_in_intern_data(index, "exact_stop", True)

    def handle_g_61_off(self, index: int) -> None:
        '''
        Deactivates G61

        Args:
            index (int):    The index of the line in the G-code file.

        Returns:
            None
        '''
        self.write_in_intern_data(index, "G_61_on", False)

    def handle_value_command(self, index: int, value_command: float) -> None:
        '''
        Handle the value command in the given line of the G-code.

        Args:
            index (int):            The index of the line in the G-code file.
            value_command (float):  The value command indicating the type of position.

        Returns:
            None
        '''
    
        # Determine the type of position command and update internal data accordingly
        match value_command:
            case 90:
                self.write_in_intern_data(index, "absolute_position", True)
            case 90.1:
                self.write_in_intern_data(index, "absolute_arc_center", True)
            case 91:
                self.write_in_intern_data(index, "absolute_position", False)
            case 91.1:
                self.write_in_intern_data(index, "absolute_arc_center", False)

    def handle_m(self, line: str, index: int) -> str:
        '''
        Handle all M-codes in a given line of the G-code.

        Args:
            line (str): The line of G-code to handle.
            index (int): The index of the line in the G-code file.

        Returns:
            str: The modified line after handling the M-codes.
        '''

        # Copy given Ms from above if this is not the first line
        columns = [
                    "spindle_on",
                    "spindle_direction",
                    "cooling_on",
                    "program_end_reached",                    
                   ]
        self.copy_from_line_above_intern_data(index, columns)
            
        line, numbers = get_numbers(line, "M", True)

        for number_index in range(len(numbers)):
            number = float(numbers[number_index])

            # match case did not work ...
            if number == CNC_Parameter.commands.get("abort"):
                self.handle_pause_program(index)

            elif number == CNC_Parameter.commands.get("quit"):
                self.handle_pause_program(index)

            elif number == CNC_Parameter.commands.get("progabort"):
                print("M" + str(number) + " not implemented jet") #TODO

            elif number == CNC_Parameter.commands.get("spindle_start_CW"):
                self.handle_spindle(index, "CW")

            elif number == CNC_Parameter.commands.get("spindle_start_CCW"):
                self.handle_spindle(index, "CCW")

            elif number == CNC_Parameter.commands.get("spindle_off"):
                self.handle_spindle(index, "off")

            elif number == CNC_Parameter.commands.get("tool_change"):
                line = self.handle_tool_change(line, index)

            elif number == CNC_Parameter.commands.get("cooling_on"):
                self.handle_cooling(index, True)

            elif number == CNC_Parameter.commands.get("cooling_off"):
                self.handle_cooling(index, False)

            elif number == CNC_Parameter.commands.get("end_of_program"):
                self.handle_end_of_program(index)

            else:
                print("M" + str(number) + " found in line " + str(index) + ". No action defined in method (handle_M)")

        return line

    def handle_pause_program(self, index: int) -> None:
        '''
        Handle pausing the program execution.

        Args:
            index (int):    The index of the line in the G-code file where the program is paused.
        
        Returns:
            None
        '''

        # Set program paused flag to True
        self.write_in_intern_data(index, "program_paused", True)
        
        # Set line importance flags
        self.write_in_intern_data(index, "important", True)
        self.write_in_visualization_data(index, "important", True)

    def handle_spindle(self, index: int, direction: str) -> None:
        '''
        Handle the spindle start or stop.

        Args:
            index (int): The index of the line in the G-code file where the spindle operation is handled.
            direction (str): The direction of spindle rotation ("CW" for clockwise, "CCW" for counterclockwise, "off" for stop).
        
        Returns:
            None
        '''

        if direction == "off":
            # Turn off the spindle
            self.write_in_intern_data(index, "spindle_on", False)
            self.write_in_intern_data(index, "spindle_direction", "")
        else:
            # Turn on the spindle
            self.write_in_intern_data(index, "spindle_on", True)
            self.write_in_intern_data(index, "spindle_direction", direction)

    # TODO: get tool data
    def handle_tool_change(self, line: str, index: int) -> str:
        '''
        Handle the tool change command.

        Args:
            line (str):     The G-code line containing the tool change command.
            index (int):    The index of the line in the G-code file.

        Returns:
            line(str):      The modified G-code line after processing the tool change command.
        '''

        line, found_T, tool_number = get_number(line, "T", delete = True)
        tool_number = int(tool_number)

        if not found_T:
            raise Exception(f"Error in g-code-line {index}: Tool change called without T")
        
        # Set the active tool number and mark tool change
        self.write_in_intern_data(index, "active_tool_number", tool_number)
        self.write_in_intern_data(index, "tool_change", True)

        # get tool data
        # TODO

        # Set line importance flags
        self.write_in_intern_data(index, "important", True)
        self.write_in_visualization_data(index, "important", True)

        return line

    def handle_cooling(self, index: int, command: bool) -> None:
        '''
        Handle the cooling command.

        Args:
            index (int): The index of the line in the G-code file.
            command (bool): The cooling command status (True for on, False for off).

        Returns:
            None
        '''

        # Set the cooling status and mark importance
        self.write_in_intern_data(index, "cooling_on", command)

        cooling_old = self.get_from_intern_data(index-1, "cooling_on")

        if command != cooling_old:
            self.write_in_intern_data(index, "cooling_change", True)
            self.write_in_intern_data(index, "important", True)
            self.write_in_visualization_data(index, "important", True)

    def handle_end_of_program(self, index: int) -> None:
        '''
        Handle the end of the program.

        Args:
            index (int):    The index of the line in the G-code file.

        Returns:
            None
        '''

        # Set the program end reached status and mark importance
        self.write_in_intern_data(index, "program_end_reached", True) 
        self.write_in_intern_data(index, "important", True)
        self.write_in_visualization_data(index, "important", True)
    
    def handle_f(self, line: str, index: int) -> str:
        '''
        Handle the F parameter in a given line of the G-code.

        Args:
            line (str):     The line of G-code to handle.
            index (int):    The index of the line in the G-code file.

        Returns:
            line (str):     The modified line after handling the F parameter.
        '''

        # Get the value of F
        line, available, value = get_number(line,  "F", True)
        value = float(value)

        # Write the value of F if available
        if available:                                                                       # F is in line
            self.write_in_intern_data(index, "F", value)                                               # write value of F in line

        return line

    def handle_s(self, line: str, index: int) -> str:
        '''
        Handle the S parameter in a given line of the G-code.

        Args:
            line (str):     The line of G-code to handle.
            index (int):    The index of the line in the G-code file.

        Returns:
            line (str):     The modified line after handling the S parameter.
        '''
        # Get the value of S
        line, available, value = get_number(line, "S", True)
        value = float(value)

        # Write the value of S or copy from the line above if available
        if available:                                                                       # F is in line
            self.write_in_intern_data(index, "S", value)                                    # write value of F in line

        return line
    
    ##################################################################################################
    # Methods: Interpreter

    # TODO: comment
    # interprets the data from the parser and fills in the rest of the columns in the DataFrame
    def interprete(self):

        self.compute_and_fill_in_spindle_speed_intern_data()
        self.compute_and_fill_in_feed_rate_intern_data()

        noflines = self.compute_needed_lines_for_all_data()

        # make dataframe: all
        self.Data_all = pd.DataFrame(np.empty(noflines, dtype = self.Col_Names_and_DataTypes_all))

        self.fill_in_all_data()

        # self.compute_expected_time_and_toolpath()

        # self.compute_expected_frequencies()

        # self.compute_other_important_stuff_for_synchronisation()

    def compute_and_fill_in_spindle_speed_intern_data(self):

        for index in range(len(self.Data_intern)):

            if index == 0:
                break
            
            spindle_on_old = self.get_from_intern_data(index-1, "spindle_on")
            spindle_on_new = self.get_from_intern_data(index, "spindle_on")
            RPM_old = self.get_from_intern_data(index-1, "S")
            RPM_new = self.get_from_intern_data(index, "S")
            
            if (spindle_on_old != spindle_on_new) or (spindle_on_new and (RPM_old != RPM_new)):
                self.write_in_intern_data(index, "important", True)
                self.write_in_visualization_data(index, "important", True)

                self.write_in_intern_data(index, "spindle_speed_change", True)

            if spindle_on_new:
                self.write_in_intern_data(index, "spindle_speed", RPM_new)
            else:
                self.write_in_intern_data(index, "spindle_speed", 0)
                
    # TODO: comment
    def compute_and_fill_in_feed_rate_intern_data(self):
        
        for index in range(len(self.Data_intern)):

            if index == 0:
                break

        # Get the movement type from the current line
        movement = self.get_from_intern_data(index, "movement")

        feed_rate = 0.0

        # If it's a rapid linear movement (G0), assign the maximum feed rate
        if movement == 0:
            feed_rate = self.CNC_Parameter.F_max
        elif movement in [1, 2, 3]:
            # For other movements (G1, G2, G3), use the specified feed rate (F) if available
            feed_rate = self.get_from_intern_data(index, "F")

        self.write_in_intern_data(index, "feed_rate", feed_rate)
    
    # TODO: improve
    def compute_needed_lines_for_all_data(self) -> int:
        '''
        Compute the lines needed for the DataFrame with all Data.

        Returns:
            int: number of needed lines for all data
        '''

        counter = 2*len(self.Data_intern)

        return counter

    # TODO: comment
    def fill_in_all_data(self) -> None:

        index_all = 0
        end_of_program = False

        for index_intern in range(len(self.Data_intern)):
            
            if index_intern == 0:
                self.add_first_line_to_all_data()
                index_all += 1

            elif self.get_from_intern_data(index_intern, "important"):

                end_of_program = self.check_end_of_program(index_intern, index_all)
                
                if end_of_program:
                    index_all += 1
                    break
                elif self.check_pause(index_intern, index_all):
                    index_all += 1
                elif self.check_dwell_time(index_intern, index_all):
                    index_all += 1
                elif self.check_tool_change(index_intern, index_all):
                    index_all += 1
                else:
                    if self.check_cooling_changes(index_intern, index_all):
                        index_all += 1
                    if self.check_spindle_speed_changes(index_intern, index_all):
                        index_all += 1
                    index_all = self.check_movement(index_intern, index_all)

    # TODO: comment
    def add_first_line_to_all_data(self):
        self.write_in_all_data(0, "what_happens", 0)

        columns = [ "movement",
                    "X", 
                    "Y", 
                    "Z", 
                    "A", 
                    "B", 
                    "C", 
                    "active_plane", 
                   ]

        for column in columns:
            value = self.get_from_intern_data(0, column)
            self.write_in_all_data(0, column, value)

    # TODO: comment
    def check_end_of_program(self, index_intern, index_all):
        if self.get_from_intern_data(index_intern, "program_end_reached"):
            self.write_in_all_data(index_all, "what_happens", 3)
            self.write_in_all_data(index_all, "program_end_reached", True)
            return True
        return False

    # TODO: comment
    def check_pause(self, index_intern, index_all):
        if self.get_from_intern_data(index_intern, "program_paused"):
            self.write_in_all_data(index_all, "program_paused", True)
            self.write_in_all_data(index_all, "what_happens", 4)
            return True
        return False

    # TODO: comment
    def check_dwell_time(self, index_intern, index_all):
        if self.get_from_intern_data(index_intern, "dwell_time"):
            self.write_in_all_data(index_all, "dwell_time", True)
            self.write_in_all_data(index_all, "what_happens", 5)
            dwell_time = self.get_from_intern_data(index_intern, "dwell_time")
            self.write_in_all_data(index_all, "dwell_time", dwell_time)
            return True
        return False
        
    # TODO: comment
    def check_tool_change(self, index_intern, index_all):
        if self.get_from_intern_data(index_intern, "tool_change"):
            self.write_in_all_data(index_all, "tool_change", True)
            self.write_in_all_data(index_all, "what_happens", 6)

            columns = [ "active_tool_number",
                        "tool_diameter",
                        "tool_length",
                    ]

            for column in columns:
                value = self.get_from_intern_data(index_intern, column)
                self.write_in_all_data(index_all, column, value)
            return True
        return False

    # TODO: comment
    def check_cooling_changes(self, index_intern, index_all):
        if self.get_from_intern_data(index_intern, "cooling_change"):
            self.write_in_all_data(index_all, "cooling_change", True)
            self.write_in_all_data(index_all, "what_happens", 7)
            cooling = self.get_from_intern_data(index_intern, "cooling_on")
            self.write_in_all_data(index_all, "cooling_on", cooling)
            return True
        return False
    
    # TODO: comment
    def check_spindle_speed_changes(self, index_intern, index_all):
        if self.get_from_intern_data(index_intern, "spindle_speed_change"):
            self.write_in_all_data(index_all, "spindle_speed_change", True)
            self.write_in_all_data(index_all, "what_happens", 8)
            RPM_new = self.get_from_intern_data(index_intern, "spindle_speed")
            self.write_in_all_data(index_all, "spindle_speed", RPM_new)
            return True
        return False

    # TODO: work and comment
    def check_movement(self, index_intern, index_all):

        if not self.get_from_intern_data(index_intern, "has_movement"):
            return index_all
        
        movement = self.get_from_intern_data(index_intern, "movement")
        linear_movement = False

        if movement in [0, 1]:
            linear_movement = True
            self.write_in_all_data(index_all, "what_happens", 1)
        else:
            self.write_in_all_data(index_all, "what_happens", 2)

        exact_stop = self.get_from_intern_data(index_intern, "exact_stop")
        if exact_stop:
            self.write_in_all_data(index_all, "exact_stop", exact_stop)
        
        position_start = self.get_start_position(index_all)
        position_end = self.get_end_position(index_intern)
        end_vector = self.get_end_vector(index_intern)
        next_start_vector = self.get_start_vector_next_movement(index_intern)

        radius_needed = vectors_same_direction(end_vector, next_start_vector)

        cutter_compensation = self.get_from_intern_data(index_intern, "cutter_compensation")

        if cutter_compensation:
            # TODO
            # compute new end point
            # add movement
            # add radius
            pass
        elif not exact_stop and radius_needed:
            # add movement
            # add radius
            # TODO
            pass
        else:
            # add movement
            # TODO
            pass
                    
        # return new index all
        return index_all

    # TODO: comment
    def add_lin_movement_from_intern_data_to_all_data(self, index_intern: int, index_all: int):

        self.write_in_all_data(index_all, "what_happens", 1)

        columns = [ "movement",
                    "X", 
                    "Y", 
                    "Z", 
                    "A", 
                    "B", 
                    "C", 
                    "feed_rate", 
                    "spindle_speed", 
                    "active_plane", 
                    "spindle_on", 
                    "spindle_direction", 
                    "active_tool_number"
                    "tool_diameter",
                    "tool_length",
                    "cooling_on",
                   ]

        for column in columns:
            value = self.get_from_intern_data(index_intern, column)
            self.write_in_all_data(index_all, column, value)

    # TODO: comment
    def add_arc_movement_from_intern_data_to_all_data(self, index_intern: int, index_all: int):

        self.write_in_all_data(index_all, "what_happens", 2)

        columns = [ "movement",
                    "X", 
                    "Y", 
                    "Z", 
                    "A", 
                    "B", 
                    "C", 
                    "I",
                    "J",
                    "K",
                    "arc_radius"
                    "arc_full_turns"
                    "feed_rate", 
                    "spindle_speed", 
                    "active_plane", 
                    "spindle_on", 
                    "spindle_direction", 
                    "active_tool_number"
                    "tool_diameter",
                    "tool_length",
                    "cooling_on",
                   ]

        for column in columns:
            value = self.get_from_intern_data(index_intern, column)
            self.write_in_all_data(index_all, column, value)

    # 1: linear movement
    # 2: arc movement
    # 3: end of program
    # 4: pause
    # 5: dwell time
    # 6: tool change
    # 7: cooling change
    # 8: RPM change
    # 9: plange change

    "index_visualisation"
    "movement"
    "X"
    "Y"
    "Z"
    "A"
    "B"
    "C"
    "I"
    "J"
    "K"
    "arc_radius"
    "arc_full_turns"
    "feed_rate"
    "spindle_speed"
    "spindle_speed_change"
    "dwell_time"
    "active_plane"
    "program_paused"  
    "spindle_on"
    "spindle_direction"
    "active_tool_number"
    "tool_diameter"
    "tool_length"
    "tool_change"
    "cooling_on"
    "program_end_reached"
    "time"

    # TODO: work and comment
    def get_start_position(self, index_all):
        return [1, 2, 3]
    
    # TODO: work and comment
    def get_end_position(self, index_intern):
        return [1, 2, 3]
    
    # TODO: work and comment
    def get_end_vector(self, index_intern):
        pass

    # TODO: work and comment
    def get_start_vector_next_movement(self, index_intern):
        return [1, 2, 3]
    
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
    
def prepare_line(line: str) -> str:
    '''
    This function prepares a line of cnc-code. It removes the \n at the end of a line, removes all spaces, removes comments and writes all letters in capital
    
    Args:
        line: line, that should be prepared

    Returns:
        The prepared line    
    '''

    line = line.strip("\n")                             # remove the \n at the end of the line if it is there
    line = line.replace(" ","")                         # remove all spaces

    if line.startswith("/"):                            # line was removed
        return ""
    
    line = line.split(";")[0]                           # remove everything behind a ; (inclusive the ;)
    line = remove_comments_in_brackets(line)            # remove comments in brackets
    line = line.upper()                                 # makes all letters upper
    return line

def remove_comments_in_brackets(line: str) -> str:
    '''
    Removes comments in round brackets () from a string

    Args:
        line: String with comments. Every open bracket must have a closing one!

    Retruns:
        line without comments in round brackets
    '''
    new_line = ""                                                                       # str to save the new line
    level = 0                                                                           # "level" of comment
    
    for char in line:                                                                   # loop the line
        if char == "(":                                                                     # start of comment found
            level +=1                                                                           # go level up
        elif char == ")":                                                                   # end of comment found
            level -=1                                                                           # go level down
        elif level == 0:                                                                    # character is not in comment
            new_line = new_line + char                                                          # add character to new line
    
    if level != 0:                                                                      # error because of inappropriate use of brackets
        raise Exception("Brackets in line not properly used: " + line)
    
    return new_line

def get_number(line, letter_combination, delete = False):
    """
    Extracts and optionally removes a number following the first given letter combination in the line.

    Args:
        line (str):                 The G-code line to search.
        letter_combination (str):   The combination of letters preceding the number.
        delete (bool, optional):    Whether to remove the letter combination and number for each occurrence. Defaults to False.

    Returns:
        tuple[str, bool, str]: A tuple with the modified line, a bool if the number was available and the extracted number for each instance of the letter combination.
    """

    line, numbers = get_numbers(line, letter_combination, delete, False)
    
    if numbers == []:
        return line, False, 0
    else:
        return line, True, numbers[0]

def get_numbers(line: str, letter_combination: str, delete: bool, all_numbers: bool = True):
    """
    Extracts all or the first number following the given letter combination in the line and optionally removes them.

    Args:
        line (str):                     The G-code line to search.
        letter_combination (str):       The combination of letters preceding the number.
        delete (bool, optional):        Whether to remove the letter combination and number.
        all_numbers (bool, optional):   Whether to extract all occurrences of the number (Default is True).

    Returns:
        tuple[str, list[str]]: A tuple of the line and a list containing the extracted numbers or an empty list if none are found.
    """
    results = []
    current_position = 0

    found_first_number = False

    while True:

        position = line.find(letter_combination, current_position)

        if position == -1:
            break
        
        if (not all_numbers) and found_first_number:
            break

        number_start = position + len(letter_combination)

        number = extract_number(line, number_start)
        
        if number == "":
            current_position = position + len(letter_combination)
        else:
            results.append(number)
            number_end = number_start + len(number)
            if delete:
                line = line[:position] + line[number_end:]
            else:
                current_position = position + len(letter_combination) 
            found_first_number = True

    return line, results

def extract_number(line: str, number_start: int) -> str:
    """
    Extracts a valid number starting from a given index in the line.

    Args:
        line (str):         The line to search for the number.
        number_start (int): The index from which to start extracting the number.

    Returns:
        str: The extracted number as a string.
    """

    if (not line) or (number_start < 0) or (number_start >= len(line)):
        return ""

    end_index = number_start

    while (end_index < len(line)) and (line[end_index] in "0123456789+-."):
        end_index += 1

    return line[number_start:end_index]

# TODO work and comment
def vectors_same_direction(v1, v2):
    pass
