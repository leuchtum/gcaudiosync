from pathlib import Path

from gcaudiosync.gcanalyser.gcanalyser import GCodeAnalyser

# Links to the test-files
src_path_g_code = Path("gcode")
src_path = src_path_g_code / "Testfall_4.cnc"

# Links to the parameters and to the snapshot
src_path_cnc_parameter = Path("readinfiles") / "parameter.txt"
src_snapshot_g_code = Path("readinfiles") / "snapshot_g_code.txt"

# Create a G_Code_Analyser
G_Code_Analyser = GCodeAnalyser(parameter_src = src_path_cnc_parameter, 
                                snapshot_src = src_snapshot_g_code)

# Analyse G-Code
G_Code_Analyser.analyse(src_path)

# Info
print(f"Duration of the G-Code according to the G_Code_Analyser: {int(G_Code_Analyser.total_duration/1000)} s")
print(f"Duration of the G-Code according to the video: ca. 130 s")

# Correction
G_Code_Analyser.set_start_time_and_total_time(0, 130000)
print(f"Duration of the G-Code according to the G_Code_Analyser after correction: {int(G_Code_Analyser.total_duration/1000)}  s")

G_Code_Analyser.generate_tool_path(fps = 10)
G_Code_Analyser.plot_tool_path()

