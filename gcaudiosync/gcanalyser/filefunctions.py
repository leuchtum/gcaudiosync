from typing import List

def read_file(src_path: str) -> List[str]:
    """
    Reads a G-code file and returns its lines as a list of strings.

    Parameters:
    -----------
    src_path : str
        The path to the G-code file.

    Returns:
    --------
    List[str]
        A list of strings representing the lines in the G-code file.
        If the file is not found or an error occurs, an empty list is returned.
    """

    try:
        # Try to open the file and read the lines
        with open(src_path, 'r') as file:
            g_code = file.readlines()

        # Remove the newline character from each line
        g_code = [line.strip("\n") for line in g_code]

        return g_code

    except FileNotFoundError:
        # Catch exception if file is not found
        print("File not found")
        return []   
    
    except Exception as e:
        # Catch all other exceptions
        print(f"An error occurred while reading the file: {e}")
        return []
    