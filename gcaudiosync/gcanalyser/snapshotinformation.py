class SnapshotInformation:

    # Constructor
    def __init__(self, 
                 g_code_line_index_start: int):
        """
        Initializes the SnapshotInformation object.

        Args:
            g_code_line_index_start: int
                Line number of the G-Code line in which the snapshot starts.
        """
    
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
