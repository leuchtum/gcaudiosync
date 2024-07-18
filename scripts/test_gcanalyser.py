from pathlib import Path

from gcaudiosync.gcanalyser.gcanalyser import GCodeAnalyser

# Links to the test-files
src_path_g_code = Path("gcode")
src_path_1 = src_path_g_code / "rechtecke.cnc"
src_path_2 = src_path_g_code / "Getriebegehaeuse.tap"
src_path_3 = src_path_g_code / "Sandbox.txt"
src_path_4 = src_path_g_code / "Testfall_1.txt"


# Links to the parameters and to the snapshot
src_path_cnc_parameter = Path("readinfiles") / "parameter.txt"
src_snapshot_g_code = Path("readinfiles") / "snapshot_g_code.txt"

# Create a G_Code_Analyser
G_Code_Analyser = GCodeAnalyser(parameter_src = src_path_cnc_parameter, 
                                snapshot_src = src_snapshot_g_code)

# Analyse G-Code
G_Code_Analyser.analyse(src_path_1)

#G_Code_Analyser.set_start_time_and_total_time(1000, 32000)
#G_Code_Analyser.adjust_start_time_of_g_code_line(3, 7000)
#G_Code_Analyser.adjust_start_time_of_g_code_line(8, 25000)
#G_Code_Analyser.adjust_start_time_of_g_code_line(5, 13000)
# G_Code_Analyser.adjust_end_time_of_g_code_line(20, 20000)

# G_Code_Analyser.Movement_Manager.print_detailed_info()

G_Code_Analyser.print_info()

#G_Code_Analyser.Sync_Info_Manager.frequency_info()

#G_Code_Analyser.Sync_Info_Manager.snapshot_info()
#G_Code_Analyser.Snapshot_Manager.print_information()

# Generate tool path
# G_Code_Analyser.generate_tool_path(fps = 10)
# G_Code_Analyser.plot_tool_path()
