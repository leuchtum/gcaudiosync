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
    line = line.replace("=","")                         # remove all equal sign

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

# TODO: comment
def find_alpha_combo(line):
    
    # check input
    if len(line) == 0:
        raise Exception("Line is empty")
    elif not line[0].isalpha() or line[0] == "_":
        raise Exception("Line does not start with an alpha: " + line)
    
    alpha_combo = ""

    for index in range(len(line)):
        character = line[index]
        if character.isalpha() or character =="_":
            alpha_combo += character
            
            if index == len(line)-1:
                line = ""
        else:
            line = line[index:]
            break
    
    return alpha_combo, line
    
# TODO: comment
def find_number(line):
    
    valid_characters = "0123456789+-."
    # check input
    if len(line) == 0:
        raise Exception("Line is empty")
    elif not line[0] in valid_characters:
        raise Exception("Line does not start with a number: " + line)
    
    number = ""

    for index in range(len(line)):
        character = line[index]
        if character in valid_characters:
            number += character
            
            if index == len(line)-1:
                line = ""
        else:
            line = line[index:]
            break
    
    return number, line
