from gcaudiosync.gcanalyser.stringfunctions import *

class LineExtractor:   
    
    # Constructor
    def __init__(self):
        pass

    #################################################################################################
    # Methods

    # TODO: work and comment
    def extract(self, line):
        # name + value, always!

        line = prepare_line(line)
        extracted_data = []

        while len(line) > 0:
            character = line[0]

            name, line = find_alpha_combo(line)

            number, line = find_number(line)
            
            extracted_data.append([name, number])
            

        return extracted_data

# end of class
#####################################################################################################