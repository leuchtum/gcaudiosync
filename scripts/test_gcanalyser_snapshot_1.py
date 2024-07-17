from pathlib import Path

from gcaudiosync.gcanalyser.gcanalyser import GCodeAnalyser

# Links to the test-files
src_path_g_code = Path("gcode")
src_path = src_path_g_code / "Testfall_2.cnc"

# Links to the parameters and to the snapshot
src_path_cnc_parameter = Path("readinfiles") / "parameter.txt"
src_snapshot_g_code = Path("readinfiles") / "snapshot_g_code.txt"

# Create a G_Code_Analyser
G_Code_Analyser = GCodeAnalyser(parameter_src = src_path_cnc_parameter, 
                                snapshot_src = src_snapshot_g_code)

# Analyse G-Code
G_Code_Analyser.analyse(src_path)

# Print real positions
print("Real positions of snapshot: g-code-line 5 and 15.")

# Print positions where snapshot was found
print("Snapshots found by G_Code_Analyser:")
G_Code_Analyser.Sync_Info_Manager.snapshot_info()

