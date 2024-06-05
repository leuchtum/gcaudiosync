from typing import List, Tuple

from gcaudiosync.gcanalyser.stringfunctions import *

class LineExtractor:   
    """
    A class to extract information from G-code lines.

    Methods:
    --------
    extract(line: str) -> List[List[str, str]]:
        Extracts commands and numbers from a G-code line.
    """

    # Constructor
    def __init__(self):
        """
        Initializes the LineExtractor instance.
        """
        pass    # Nothing to initialize

    #################################################################################################
    # Methods

    def extract(self, line: str) -> List[Tuple[str, str]]:
        """
        Extracts commands and numbers from a G-code line.

        Parameters:
        -----------
        line : str
            The G-code line to extract information from.

        Returns:
        --------
        List[List[str, str]]
            A list of lists where each sublist contains a command and its associated number.
        """

        line = prepare_line(line)  # Prepare the line for extraction
        extracted_data: List[List[str, str]] = []  # List to store the extracted data

        # Extract until no data left
        while len(line) > 0:
            command, line = find_alpha_combo(line)      # Get the alpha combo at front of the line and the line without this combo
            number, line = find_number(line)            # Get the number at fromt of the line and the line without this number
            extracted_data.append([command, number])    # Add extracted command and number to the extracted data
            
        return extracted_data

# End of class
###################################################################################################
