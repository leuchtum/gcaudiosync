
from pathlib import Path
from gcaudiosync.gcanalyser.gcanalyser import GCodeAnalyser

# links to the test-files
src_path_g_code = Path("gcode")
src_path_1 = src_path_g_code / "rechtecke.cnc"
src_path_2 = src_path_g_code / "Getriebegehaeuse.tap"

src_path_cnc_parameter = Path("cncparameter") / "parameter.txt"

# create a G_Code_Analyser
G_Code_Analyser = GCodeAnalyser(src_path_cnc_parameter)

# analyse G-Code
G_Code_Analyser.analyse(src_path_2)

print(G_Code_Analyser.g_code)

print(G_Code_Analyser.Frequancy_Manager.frequencies)

# print visualisation data
# print(G_Code.Data_visualisation)
# print(G_Code.Data_all)
# print(G_Code.toolpath)