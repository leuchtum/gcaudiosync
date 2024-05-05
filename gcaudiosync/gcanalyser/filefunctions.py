
# Function to read in a cnc-file
def read_file(src_path: str):
    # Try to open the file and read the lines
    try:
        with open(src_path) as file:
            g_code = file.readlines()

        # Remove the \n in each line
        for index, line in enumerate(g_code):
            g_code[index] = line.strip("\n")
        return g_code
    except FileNotFoundError:   # Catch exception if file is not found
        print("File not found")
        return []
    except Exception as e:  # Catch all other exceptions
        print(f"An error occurred while reading the file: {e}")
        return []
    