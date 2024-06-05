from pathlib import Path

from gcaudiosync.gcanalyser.gcanalyser import GCodeAnalyser

# links to the test-files
src_path_g_code = Path("gcode")
src_path_1 = src_path_g_code / "rechtecke.cnc"
src_path_2 = src_path_g_code / "Getriebegehaeuse.tap"
src_path_3 = src_path_g_code / "Sandbox.txt"

src_path_cnc_parameter = Path("cncparameter") / "parameter.txt"

# create a G_Code_Analyser
G_Code_Analyser = GCodeAnalyser(src_path_cnc_parameter)

# analyse G-Code
G_Code_Analyser.analyse(src_path_1)

G_Code_Analyser.set_start_time_and_total_time(1000, 40000)
G_Code_Analyser.adjust_start_time_of_g_code_line(15, 15000)
G_Code_Analyser.adjust_end_time_of_g_code_line(20, 20000)

G_Code_Analyser.Movement_Manager.print_info()

time = 0
for movement in G_Code_Analyser.Movement_Manager.movements:
    time += movement.time

print(time)

# generate tool path
G_Code_Analyser.generate_tool_path(10)
G_Code_Analyser.plot_tool_path()
