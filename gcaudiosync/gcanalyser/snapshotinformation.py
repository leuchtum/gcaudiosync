class SnapshotInformation:

    # Constructor
    def __init__(self, 
                 g_code_line_index_start: int):
    
        self.g_code_line_index_start: int = g_code_line_index_start
        self.expected_time_start: float = 0.0

    #################################################################################################
    # Methods

    def info(self) -> None:
        """
        Prints the info of the snapshot
        """

        print(f"Snapshot in g-code-line {self.g_code_line_index_start}")

    # End of class
#####################################################################################################
