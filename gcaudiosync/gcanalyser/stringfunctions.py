
def prepare_line(line: str) -> str:
    '''
    This function prepares a line of cnc-code. It removes the \n at the end of a line, removes all spaces, removes comments and writes all letters in capital
    
    Args:
        line: line, that should be prepared

    Returns:
        The prepared line    
    '''

    line = line.strip("\n")                             # Remove the \n at the end of the line if it is there
    line = line.replace(" ","")                         # Remove all spaces
    line = line.replace("=","")                         # Remove all equal sign

    if line.startswith("/"):                            # Line was removed
        return ""
    
    line = line.split(";")[0]                           # Remove everything behind a ; (inclusive the ;)
    line = remove_comments_in_brackets(line)            # Remove comments in brackets
    line = line.upper()                                 # Makes all letters upper
    return line

def remove_comments_in_brackets(line: str) -> str:
    '''
    Removes comments in round brackets () from a string

    Args:
        line: String with comments. Every open bracket must have a closing one!

    Retruns:
        line without comments in round brackets
    '''
    new_line = ""                                                       # Str to save the new line
    level = 0                                                           # "Level" of comment
    
    for char in line:                                                   # Loop the line
        if char == "(":                                                     # Start of comment found
            level +=1                                                           # Go level up
        elif char == ")":                                                   # End of comment found
            level -=1                                                           # Go level down
        elif level == 0:                                                    # Character is not in comment
            new_line = new_line + char                                          # Add character to new line
    
    if level != 0:                                                      # Error because of inappropriate use of brackets
        raise Exception("Brackets in line not properly used: " + line)      # raise Error
    
    return new_line

# Function to find a alpha combo in front of a str
def find_alpha_combo(line: str):
    
    # Check input
    if len(line) == 0:
        raise Exception("Line is empty")
    elif not line[0].isalpha() or line[0] == "_":
        raise Exception("Line does not start with an alpha: " + line)
    
    # Define empty alpha combo and line for return
    alpha_combo: str    = ""
    new_line: str       = line

    # Go through line
    for index in range(len(line)):

        character = line[index]                     # Get character

        if character.isalpha() or character =="_":  # Character is part of a alpha_combo
            alpha_combo += character                    # Add character to alpha_combo
            
            if index == len(line)-1:                    # End of line reached
                new_line = ""                               # Make line empty
        else:                                       # Character is not part of a alpha-combo
            new_line = new_line[index:]                 # Shorten the line
            break                                       # Break the loop
    
    return alpha_combo, new_line
    
# Function to find a number in fromt of a str
def find_number(line):
    
    valid_characters = "0123456789+-."                                  # valid characters

    # check input
    if len(line) == 0:
        raise Exception("Line is empty")
    elif not line[0] in valid_characters:
        raise Exception("Line does not start with a number: " + line)
    
    # Define empty number and line for return
    number: str         = ""
    new_line: str       = line

    # Go through line
    for index in range(len(line)):  

        character = line[index]             # Get character

        if character in valid_characters:   # Character is part of a number
            number += character                 # Add character to number
            
            if index == len(line)-1:            # End of line reached
                new_line = ""                       # Make line empty
        else:                               # Character is not part of a number
            new_line = new_line[index:]         # Shorten line
            break                               # break loop
    
    return number, new_line
