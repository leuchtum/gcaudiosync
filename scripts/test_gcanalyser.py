from pathlib import Path

from matplotlib import pyplot as plt

# Import the G-Code-Analyser
from gcaudiosync.gcanalyser.gcanalyser import GCodeAnalyser
from gcaudiosync.gcanalyser.toolpathgenerator import AlternativeToolPathAnimator

# Links to the test-file
src_path_g_code = Path("gcode")
src_path_1 = src_path_g_code / "rechtecke.cnc"

# Links to the parameters and to the snapshot
src_path_cnc_parameter = Path("readinfiles") / "parameter.txt"
src_snapshot_g_code = Path("readinfiles") / "snapshot_g_code.txt"

# Create a G_Code_Analyser
G_Code_Analyser = GCodeAnalyser(
    parameter_src=src_path_cnc_parameter, snapshot_src=src_snapshot_g_code
)

# Analyse G-Code
G_Code_Analyser.analyse(src_path_1)

# Read the important informations of the g-code analysed by the GCodeAnalyser
# List containing all the information about the frequencies:
Frequency_Information_List = G_Code_Analyser.Sync_Info_Manager.frequency_information
# List containing all the information about the snapshots:
Snapshot_Information_List = G_Code_Analyser.Sync_Info_Manager.snapshot_information

# Adjust the G-Code
G_Code_Analyser.set_start_time_and_total_time(1000, 50000)
G_Code_Analyser.adjust_start_time_of_g_code_line(11, 2500)
G_Code_Analyser.adjust_start_time_of_g_code_line(24, 30000)

# Print generel informations (optional)
G_Code_Analyser.print_info()

# Print out all the Movement details (optional)
G_Code_Analyser.Movement_Manager.print_detailed_info()

# Print out the frequency-informations (optional)
G_Code_Analyser.Sync_Info_Manager.frequency_info()

# Print out the snapshot-informations (optional)
G_Code_Analyser.Sync_Info_Manager.snapshot_info()

# Generate and plot toolpath
use_alternative_toolpath_animator = True

if use_alternative_toolpath_animator:
    fig = plt.figure(figsize=(8, 5))
    ax_info = fig.add_subplot(1, 3, 1)
    ax_tool = fig.add_subplot(1, 3, (2, 3))

    toolpath_ani = AlternativeToolPathAnimator(
        G_Code_Analyser.Movement_Manager,
        G_Code_Analyser.g_code,
        ax_tool,
        ax_info,
        60,
    )
    toolpath_ani.run()
    plt.show()
else:
    G_Code_Analyser.generate_tool_path(fps=10)
    G_Code_Analyser.plot_tool_path(version="Haas")
