from gcaudiosync.gcanalyser.stringfunctions import *

class Line_Extractor:   
    
    # Constructor
    def __init__(self):
        pass    # nothing to do

    #################################################################################################
    # Methods

    # Method to extract all commands and numbers in a line. Important: always command + number
    def extract(self, line: str):

        line: str = prepare_line(line)      # Prepare line for the extraction
        extracted_data:list = []            # Empty list for all the extracted data

        # Extract until no data left
        while len(line) > 0:

            command, line = find_alpha_combo(line)      # Get the alpha combo at front of the line and the line without this combo

            number, line = find_number(line)            # Get the number at fromt of the line and the line without this number

            extracted_data.append([command, number])    # Add extracted command and number to the extracted data
            

        return extracted_data

# End of class
###################################################################################################