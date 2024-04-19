
# TODO: comment
def read_file(src_path: str):
    try:
        with open(src_path) as file:
            g_code = file.readlines()

        for index, line in enumerate(g_code):
            g_code[index] = line.strip("\n")
        return g_code
    except FileNotFoundError:
        print("File not found")
        return []
    except Exception as e:  # Catch all other exceptions
        print(f"An error occurred while reading the file: {e}")
        return []
    