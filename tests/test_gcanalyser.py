import math

import numpy as np
import pandas as pd

from src.gcanalyser import GCodeAnalyser

# links to the test-files
src_path_1 =  '...\\rechtecke.cnc'
src_path_2 =  '...\\Getriebegehaeuse.tap'

# create a G_Code_Analyser
G_Code = GCodeAnalyser()

# analyse G-Code
G_Code.analyse(src_path_1)