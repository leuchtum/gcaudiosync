
from pathlib import Path
from gcaudiosync.gcanalyser.gcanalyser import GCodeAnalyser

# links to the test-files
src_path = Path("gcode")
src_path_1 = src_path / "rechtecke.cnc"
src_path_2 = src_path / "Getriebegehaeuse.tap"

# create a G_Code_Analyser
G_Code = GCodeAnalyser()

# analyse G-Code
G_Code.analyse(src_path_1)